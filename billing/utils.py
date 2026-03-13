def has_basic(user):
    return user.subscription.tier == "basic" and user.subscription.is_active()

def has_pro(user):
    return user.subscription.tier == "pro" and user.subscription.is_active()

def has_enterprise(user):
    return user.subscription.tier == "enterprise" and user.subscription.is_active()

def user_tier(user):
    if not hasattr(user, "subscription"):
        return None
    if not user.subscription.is_active():
        return None
    return user.subscription.tier

def can_send_messages(user):
    tier = user_tier(user)

    # Enterprise: unlimited
    if tier == "enterprise":
        return True

    # Pro: unlimited or high limit
    if tier == "pro":
        return True

    # Basic: limited by credits
    if tier == "basic":
        return user.profile.message_credits > 0

    return False

def can_access_analytics(user):
    return user_tier(user) in ["pro", "enterprise"]

def get_stripe_subscription(profile):
    return profile.stripe_subscription

def can_add_multiple_stores(user):
    return user_tier(user) == "enterprise"
    

def record_message_usage(user):
    profile = user.profile

    # Basic plan uses credits
    if user_tier(user) == "basic":
        profile.message_credits -= 1
        profile.save()

    # Metered billing (optional)
    if hasattr(user.subscription, "metered_item_id"):
        stripe.UsageRecord.create(
            quantity=1,
            timestamp=int(time.time()),
            action="increment",
            subscription_item=user.subscription.metered_item_id,
        )

    if not can_access_analytics(request.user):
        return redirect("upgrade_required")
    
def plan_summary(user):
    sub = getattr(user, "subscription", None)
    if not sub or not sub.is_active():
        return {
            "tier": None,
            "active": False,
            "credits": user.profile.message_credits,
        }

    return {
        "tier": sub.tier,
        "active": True,
        "credits": user.profile.message_credits,
        "next_payment": sub.current_period_end,
        "status": sub.status,
    }
