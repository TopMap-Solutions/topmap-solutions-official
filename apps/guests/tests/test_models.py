from django.test import TestCase

from apps.guests.models import Guest


class GuestModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.guest = Guest.objects.create(
            organization="topmap",
            name="joshua",
            email="email@email.com",
            phone="092323233",
            inquiry="I need a GIS system.",
        )

    def test_guest_is_created(self):
        """Guest is created successfully."""
        self.assertEqual(Guest.objects.count(), 1)

    def test_guest_fields(self):
        """Guest fields contain expected values."""
        self.assertEqual(self.guest.name, "joshua")
        self.assertEqual(self.guest.email, "email@email.com")
        self.assertEqual(self.guest.organization, "topmap")

    def test_guest_defaults(self):
        """Guest default values are correct."""
        self.assertFalse(self.guest.contacted)

    def test_guest_string_representation(self):
        """Guest string representation is correct."""
        self.assertEqual(
            str(self.guest),
            "joshua - topmap (email@email.com)",
        )
