from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest.mock import patch


@patch("accounts.signals.stripe.Customer.create")
class ProfileModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create shared fixtures for Profile model tests."""
        cls.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        # Use the auto-created profile from the signal
        cls.profile = cls.user.profile

    def test_profile_str_returns_full_name_when_present(self, mock_stripe):
        self.profile.full_name = "Test User"
        self.profile.save()
        self.assertEqual(str(self.profile), "Test User")

    def test_profile_str_returns_username_when_full_name_empty(
        self,
        mock_stripe,
    ):
        self.profile.full_name = ""
        self.profile.save()
        self.assertEqual(str(self.profile), "testuser")

    def test_default_role_is_owner(self, mock_stripe):
        self.assertEqual(self.profile.role, "owner")

    def test_default_message_credits_is_zero(self, mock_stripe):
        self.assertEqual(self.profile.message_credits, 0)
