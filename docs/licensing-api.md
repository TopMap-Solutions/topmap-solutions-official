# Licensing API

The public licensing API supports manually issued licenses for TopMap desktop
plugins. It does not process payments. Staff create products and licenses in
Django admin at `admin`.

## Administration

1. Create a **Licensed product** with the stable code used by the plugin, such
   as `parcel-buddy`.
2. Create a **License**, choose its term and activation limit, and save it.
3. Copy the generated key from the warning message immediately. Only a keyed
   digest and a short hint are stored, so the full key cannot be recovered.
4. Use the state field to suspend or revoke access. Activation and audit rows
   are read-only in admin.

Available terms are 14 days, one month, three months, one year, and lifetime.
The term begins on first successful activation. Calendar months are used for
monthly and yearly terms.

## Endpoints

All mutation endpoints require `POST` and `Content-Type: application/json`.
Responses use `Cache-Control: no-store`. Production must only expose them over
HTTPS.

- `GET /api/v1/licensing/health/`
- `POST /api/v1/licensing/activate/`
- `POST /api/v1/licensing/validate/`
- `POST /api/v1/licensing/deactivate/`

Activation body:

```json
{
  "license_key": "TM-...",
  "product_code": "parcel-buddy",
  "installation_id": "random-id-persisted-by-the-plugin",
  "device_fingerprint": "privacy-conscious-stable-device-value",
  "plugin_version": "1.0.0"
}
```

A successful response includes an opaque `activation_token`. Store it using
operating-system protected storage and send it to validation:

```json
{
  "activation_token": "opaque-server-signed-value",
  "product_code": "parcel-buddy",
  "installation_id": "random-id-persisted-by-the-plugin",
  "device_fingerprint": "privacy-conscious-stable-device-value",
  "plugin_version": "1.0.0"
}
```

Deactivation needs the token, product code, and installation ID. A successful
deactivation permits that license slot to be activated again.

## Client rules

- Treat server time and the returned `valid` value as authoritative.
- Do not place `SECRET_KEY` or another shared server secret in the plugin.
- Treat activation tokens as credentials and never log them.
- Generate the installation ID randomly; do not use a person's name or email.
- Build a fingerprint from the minimum stable machine information needed and
  tell customers what is collected.
- Revalidate regularly and define any offline grace policy in the plugin and
  customer terms. The first API release does not claim tamper-proof offline
  validation.

## Security and operations

The API validates request size and fields, rate-limits by endpoint and remote
address, uses transactional activation limits, stores no plaintext license key,
hashes fingerprints and remote addresses, signs activation tokens, and records
security events. Native desktop clients do not use browser cookies, so these
JSON endpoints are CSRF-exempt; they do not enable cross-origin browser access.

Configure these optional environment values:

```text
LICENSING_TOKEN_MAX_AGE_SECONDS=2592000
LICENSING_RATE_LIMIT=25
LICENSING_RATE_WINDOW_SECONDS=25
LICENSING_KEY_PEPPER=a-separate-high-entropy-secret
LICENSING_TRUST_PROXY_HEADERS=false
```

The default Django cache is process-local. For multiple web instances, configure
a shared production cache before relying on the rate limit as a perimeter
control, and also apply limits at the reverse proxy or firewall. The application
default is 25 requests across all licensing API endpoints per client IP address
per 25 seconds; a rejected request returns HTTP 429 with `Retry-After: 25`.

By default the application uses the direct network address and ignores the
spoofable `X-Forwarded-For` header. If the deployment has a trusted reverse proxy
that overwrites (rather than appends untrusted input to) that header, set
`LICENSING_TRUST_PROXY_HEADERS=true`. Otherwise all users may appear to come from
the proxy and share one limit. Apply the same or stricter limit at that proxy;
application limiting reduces abuse but cannot absorb a network-level DDoS.

Back up the
database, `SECRET_KEY`, and `LICENSING_KEY_PEPPER`. Changing `SECRET_KEY`
invalidates active tokens but customers can activate again. Changing or losing
`LICENSING_KEY_PEPPER` makes previously issued keys impossible to look up. Set a
dedicated pepper before issuing the first production license and retain it during
deployments and key rotation.

