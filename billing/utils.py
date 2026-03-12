def has_basic(user):
    return user.subscription.tier == "basic" and user.subscription.is_active()

def has_pro(user):
    return user.subscription.tier == "pro" and user.subscription.is_active()

def has_enterprise(user):
    return user.subscription.tier == "enterprise" and user.subscription.is_active()
