from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from stores.models import Store, StoreMember


class StoreModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        stripe_customer = Mock()
        stripe_customer.id = "cus_test_store_owner"

        with patch(
            "accounts.signals.stripe.Customer.create",
            return_value=stripe_customer,
        ):
            cls.owner = get_user_model().objects.create_user(
                username="store-owner",
                email="owner@example.com",
                password="testpass123",
            )

        with patch("stores.signals.generate_store_qr"):
            cls.store = Store.objects.create(
                owner=cls.owner,
                name="Meridian Market",
                description="Primary storefront",
                website="https://example.com",
            )

    def test_store_can_be_created(self):
        self.assertIsInstance(self.store, Store)
    def test_store_has_owner(self):
        self.assertEqual(self.store.owner, self.owner)
    def test_store_has_name_and_description(self):
        self.assertEqual(self.store.name, "Meridian Market")
        self.assertEqual(self.store.description, "Primary storefront")

    def test_store_str_returns_name(self):
        self.assertEqual(str(self.store), self.store.name)

    def test_store_generates_slug_when_blank(self):
        self.store.slug = ""
        self.store.save()
        self.assertEqual(self.store.slug, "store-owner-meridian-market")

    def test_store_allows_optional_branding_fields(self):
        self.store.logo = None
        self.store.tagline = ""
        self.store.save()
        self.assertFalse(self.store.logo)
        self.assertEqual(self.store.tagline, "")

    def test_store_tracks_creation_timestamp(self):
        self.assertIsNotNone(self.store.created_at)


class StoreMemberModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        owner_customer = Mock()
        owner_customer.id = "cus_test_member_owner"

        with patch(
            "accounts.signals.stripe.Customer.create",
            return_value=owner_customer,
        ):
            cls.owner = get_user_model().objects.create_user(
                username="member-store-owner",
                email="member-owner@example.com",
                password="testpass123",
            )

        member_customer = Mock()
        member_customer.id = "cus_test_member_user"

        with patch(
            "accounts.signals.stripe.Customer.create",
            return_value=member_customer,
        ):
            cls.user = get_user_model().objects.create_user(
                username="store-staff",
                email="staff@example.com",
                password="testpass123",
            )

        cls.store = Store.objects.create(
            owner=cls.owner,
            name="Member Store",
        )
        cls.membership = StoreMember.objects.create(
            store=cls.store,
            user=cls.user,
        )

    def test_store_member_can_be_created(self):
        self.assertIsInstance(self.membership, StoreMember)

    def test_store_member_str_describes_membership(self):
        expected_str = f"{self.user.username} → {self.store.name}"
        self.assertEqual(str(self.membership), expected_str)

    def test_store_member_links_user_to_store(self):
        self.assertEqual(self.membership.user, self.user)
        self.assertEqual(self.membership.store, self.store)

    def test_store_member_defaults_role_to_staff(self):
        self.assertEqual(self.membership.role, "staff")

    def test_store_member_enforces_unique_store_user_pair(self):
        with self.assertRaises(Exception):
            StoreMember.objects.create(
                store=self.store,
                user=self.user,
            )

    def test_store_member_tracks_when_membership_was_added(self):
        self.assertIsNotNone(self.membership.added_at)
