from time import time

import stripe


def _get_subscription(user):
    return getattr(user, "subscription", None)


def has_basic(user):
    subscription = _get_subscription(user)
    return bool(
        subscription
        and subscription.tier == "basic"
        and subscription.is_active()
    )


def has_pro(user):
    subscription = _get_subscription(user)
    return bool(
        subscription
        and subscription.tier == "pro"
        and subscription.is_active()
    )


def has_enterprise(user):
    subscription = _get_subscription(user)
    return bool(
        subscription
        and subscription.tier == "enterprise"
        and subscription.is_active()
    )


def user_tier(user):
    subscription = _get_subscription(user)
    if not subscription or not subscription.is_active():
        return None
    return subscription.tier


def can_send_messages(user):
    tier = user_tier(user)

    if tier in {"enterprise", "pro"}:
        return True

    if tier == "basic":
        return user.profile.message_credits > 0

    return False


def can_access_analytics(user):
    return user_tier(user) in ["pro", "enterprise"]


def get_stripe_subscription(user):
    return _get_subscription(user)


def can_add_multiple_stores(user):
    return user_tier(user) == "enterprise"


def record_message_usage(user):
    profile = user.profile
    subscription = _get_subscription(user)

    if user_tier(user) == "basic":
        profile.message_credits -= 1
        profile.save(update_fields=["message_credits"])

    if subscription and hasattr(subscription, "metered_item_id"):
        stripe.UsageRecord.create(
            quantity=1,
            timestamp=int(time()),
            action="increment",
            subscription_item=subscription.metered_item_id,
        )


def plan_summary(user):
    subscription = _get_subscription(user)
    if not subscription or not subscription.is_active():
        return {
            "tier": None,
            "active": False,
            "credits": user.profile.message_credits,
        }

    return {
        "tier": subscription.tier,
        "active": True,
        "credits": user.profile.message_credits,
        "next_payment": subscription.current_period_end,
        "status": subscription.status,
    }
