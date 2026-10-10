import json
from datetime import datetime, timedelta, timezone as dt_timezone

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.licensing.models import License, LicenseActivation, LicensedProduct


class LicenseTermTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = LicensedProduct.objects.create(
            name="Parcel Buddy", code="parcel-buddy"
        )

    def test_all_supported_terms_calculate_from_first_activation(self):
        activated_at = datetime(2027, 1, 31, 8, 0, tzinfo=dt_timezone.utc)
        expected = {
            License.Term.DAYS_14: datetime(2027, 2, 14, 8, 0, tzinfo=dt_timezone.utc),
            License.Term.MONTH_1: datetime(2027, 2, 28, 8, 0, tzinfo=dt_timezone.utc),
            License.Term.MONTHS_3: datetime(2027, 4, 30, 8, 0, tzinfo=dt_timezone.utc),
            License.Term.YEAR_1: datetime(2028, 1, 31, 8, 0, tzinfo=dt_timezone.utc),
            License.Term.LIFETIME: None,
        }
        for term, expires_at in expected.items():
            with self.subTest(term=term):
                license_obj = License(product=self.product, term=term)
                license_obj.activate_term(activated_at)
                self.assertEqual(license_obj.expires_at, expires_at)


@override_settings(LICENSING_RATE_LIMIT=100, LICENSING_TOKEN_MAX_AGE_SECONDS=2592000)
class LicensingApiTests(TestCase):
    def setUp(self):
        cache.clear()
        self.product = LicensedProduct.objects.create(
            name="Parcel Buddy", code="parcel-buddy"
        )
        self.license = License(product=self.product, term=License.Term.MONTH_1)
        self.license.save()
        self.raw_key = self.license._generated_key
        self.activation_data = {
            "license_key": self.raw_key,
            "product_code": "parcel-buddy",
            "installation_id": "install-001",
            "device_fingerprint": "safe-device-fingerprint",
            "plugin_version": "1.0.0",
        }

    def post_json(self, path, data):
        return self.client.post(path, json.dumps(data), content_type="application/json")

    def activate(self):
        return self.post_json("/api/v1/licensing/activate/", self.activation_data)

    def test_activation_sets_expiry_and_returns_opaque_token(self):
        response = self.activate()
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["status"], "active")
        self.assertTrue(payload["activation_token"])
        self.assertEqual(response["Cache-Control"], "no-store")
        self.license.refresh_from_db()
        self.assertIsNotNone(self.license.activated_at)
        self.assertIsNotNone(self.license.expires_at)

    def test_key_is_not_stored_in_plaintext(self):
        self.assertNotEqual(self.license.key_digest, self.raw_key)
        self.assertNotIn(self.raw_key, self.license.key_hint)

    def test_validate_refreshes_a_valid_activation(self):
        token = self.activate().json()["activation_token"]
        data = {
            k: self.activation_data[k]
            for k in (
                "product_code",
                "installation_id",
                "device_fingerprint",
                "plugin_version",
            )
        }
        data["activation_token"] = token
        response = self.post_json("/api/v1/licensing/validate/", data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["valid"])

    def test_tampered_token_and_device_are_rejected(self):
        token = self.activate().json()["activation_token"]
        data = {
            "activation_token": token + "tampered",
            "product_code": "parcel-buddy",
            "installation_id": "install-001",
            "device_fingerprint": "safe-device-fingerprint",
        }
        self.assertEqual(
            self.post_json("/api/v1/licensing/validate/", data).status_code, 403
        )
        data["activation_token"] = token
        data["device_fingerprint"] = "different-device"
        self.assertEqual(
            self.post_json("/api/v1/licensing/validate/", data).status_code, 403
        )

    def test_activation_limit_blocks_another_installation(self):
        self.assertEqual(self.activate().status_code, 200)
        other = {**self.activation_data, "installation_id": "install-002"}
        self.assertEqual(
            self.post_json("/api/v1/licensing/activate/", other).status_code, 403
        )

    def test_revoked_and_expired_licenses_are_rejected(self):
        token = self.activate().json()["activation_token"]
        self.license.refresh_from_db()
        self.license.state = License.State.REVOKED
        self.license.save(update_fields=("state",))
        data = {
            "activation_token": token,
            "product_code": "parcel-buddy",
            "installation_id": "install-001",
            "device_fingerprint": "safe-device-fingerprint",
        }
        self.assertEqual(
            self.post_json("/api/v1/licensing/validate/", data).status_code, 403
        )
        self.license.state = License.State.ENABLED
        self.license.expires_at = timezone.now() - timedelta(seconds=1)
        self.license.save(update_fields=("state", "expires_at"))
        self.assertEqual(self.activate().status_code, 403)

    def test_deactivation_frees_the_activation(self):
        token = self.activate().json()["activation_token"]
        response = self.post_json(
            "/api/v1/licensing/deactivate/",
            {
                "activation_token": token,
                "product_code": "parcel-buddy",
                "installation_id": "install-001",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(LicenseActivation.objects.get().is_active)

    def test_invalid_content_type_and_oversized_values_are_rejected(self):
        self.assertEqual(
            self.client.post(
                "/api/v1/licensing/activate/", self.activation_data
            ).status_code,
            400,
        )
        bad = {**self.activation_data, "installation_id": "x" * 129}
        self.assertEqual(
            self.post_json("/api/v1/licensing/activate/", bad).status_code, 400
        )


@override_settings(LICENSING_RATE_LIMIT=1, LICENSING_RATE_WINDOW_SECONDS=25)
class LicensingRateLimitTests(TestCase):
    def test_repeated_requests_are_rate_limited(self):
        cache.clear()
        data = {
            "license_key": "bad",
            "product_code": "x",
            "installation_id": "x",
            "device_fingerprint": "x",
        }
        self.client.post(
            "/api/v1/licensing/activate/",
            json.dumps(data),
            content_type="application/json",
        )
        response = self.client.post(
            "/api/v1/licensing/activate/",
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response["Retry-After"], "25")

    def test_limit_is_shared_across_licensing_endpoints_for_the_same_ip(self):
        cache.clear()
        data = {
            "license_key": "bad",
            "product_code": "x",
            "installation_id": "x",
            "device_fingerprint": "x",
        }
        self.client.post(
            "/api/v1/licensing/activate/",
            json.dumps(data),
            content_type="application/json",
        )
        response = self.client.post(
            "/api/v1/licensing/validate/",
            json.dumps(
                {
                    "activation_token": "bad",
                    "product_code": "x",
                    "installation_id": "x",
                    "device_fingerprint": "x",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 429)
