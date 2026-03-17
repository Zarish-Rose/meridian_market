from datetime import timezone as datetime_timezone
import json

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from unittest.mock import Mock, patch

from billing.models import StripeSubscription
from billing.webhooks import _stripe_timestamp_to_datetime


class SubscriptionModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        stripe_customer = Mock()
        stripe_customer.id = "cus_test_123"

        with patch(
            "accounts.signals.stripe.Customer.create",
            return_value=stripe_customer,
        ):
            cls.user = get_user_model().objects.create_user(
                username="subscription-user",
                email="subscription@example.com",
                password="testpass123",
            )

        cls.subscription = StripeSubscription.objects.create(
            user=cls.user,
            stripe_subscription_id="sub_test_123",
            price_id="price_test_123",
            tier="basic",
            status="active",
        )

    def test_subscription_can_be_created_for_user(self):
        subscription = self.subscription

        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.stripe_subscription_id, "sub_test_123")
        self.assertEqual(subscription.price_id, "price_test_123")
        self.assertEqual(subscription.tier, "basic")
        self.assertEqual(subscription.status, "active")

    def test_subscription_allows_nullable_billing_fields(self):
        stripe_customer = Mock()
        stripe_customer.id = "cus_test_456"

        with patch(
            "accounts.signals.stripe.Customer.create",
            return_value=stripe_customer,
        ):
            user = get_user_model().objects.create_user(
                username="nullable-user",
                email="nullable@example.com",
                password="testpass123",
            )

        subscription = StripeSubscription.objects.create(user=user)

        self.assertIsNone(subscription.stripe_subscription_id)
        self.assertIsNone(subscription.price_id)
        self.assertIsNone(subscription.tier)
        self.assertIsNone(subscription.status)
        self.assertIsNone(subscription.current_period_end)

    def test_tier_accepts_expected_choice_values(self):
        expected_choices = {"basic", "pro", "enterprise"}
        actual_choices = {
            value for value, _label in StripeSubscription.TIER_CHOICES
        }

        self.assertSetEqual(actual_choices, expected_choices)

        for tier in expected_choices:
            subscription = StripeSubscription(user=self.user, tier=tier)
            subscription.full_clean(exclude=["user"])

        with self.assertRaises(ValidationError):
            invalid_subscription = StripeSubscription(
                user=self.user,
                tier="invalid",
            )
            invalid_subscription.full_clean(exclude=["user"])

    def test_is_active_returns_true_for_active_status(self):
        self.subscription.status = "active"

        self.assertTrue(self.subscription.is_active())

    def test_is_active_returns_true_for_trialing_status(self):
        self.subscription.status = "trialing"

        self.assertTrue(self.subscription.is_active())

    def test_is_active_returns_false_for_inactive_statuses(self):
        for status in [None, "canceled", "past_due", "incomplete"]:
            with self.subTest(status=status):
                self.subscription.status = status
                self.assertFalse(self.subscription.is_active())

    def test_subscription_is_unique_per_user(self):
        with self.assertRaises(IntegrityError):
            StripeSubscription.objects.create(user=self.user)


class BillingWebhookTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        stripe_customer = Mock()
        stripe_customer.id = "cus_webhook_123"

        with patch(
            "accounts.signals.stripe.Customer.create",
            return_value=stripe_customer,
        ):
            cls.user = get_user_model().objects.create_user(
                username="webhook-user",
                email="webhook@example.com",
                password="testpass123",
            )

        cls.profile = cls.user.profile
        cls.profile.stripe_customer_id = stripe_customer.id
        cls.profile.save(update_fields=["stripe_customer_id"])

    def test_stripe_timestamp_to_datetime_returns_utc_datetime(self):
        converted = _stripe_timestamp_to_datetime(1742169600)

        self.assertIsNotNone(converted)
        self.assertTrue(timezone.is_aware(converted))
        self.assertEqual(converted.tzinfo, datetime_timezone.utc)

    @patch("billing.webhooks.stripe.Webhook.construct_event")
    def test_webhook_stores_current_period_end_as_datetime(
        self,
        construct_event,
    ):
        construct_event.return_value = {
            "type": "customer.subscription.created",
            "data": {
                "object": {
                    "id": "sub_webhook_123",
                    "customer": self.profile.stripe_customer_id,
                    "status": "active",
                    "current_period_end": 1742169600,
                    "items": {
                        "data": [
                            {"price": {"id": "price_basic"}},
                        ]
                    },
                }
            },
        }

        with self.settings(STRIPE_PRICE_TO_TIER={"price_basic": "basic"}):
            response = self.client.post(
                "/billing/webhook/",
                data=json.dumps({"id": "evt_test"}),
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="sig_test",
            )

        self.assertEqual(response.status_code, 200)

        subscription = StripeSubscription.objects.get(user=self.user)
        self.assertEqual(subscription.tier, "basic")
        self.assertTrue(timezone.is_aware(subscription.current_period_end))
        self.assertEqual(
            subscription.current_period_end,
            _stripe_timestamp_to_datetime(1742169600),
        )
