from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from billing.utils import can_send_messages, user_tier


def subscription_required(view_func):
    def wrapper(request, *args, **kwargs):
        subscription = getattr(request.user, "subscription", None)
        if not subscription or not subscription.is_active():
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper


def require_tier(min_tier):
    tier_order = [None, "basic", "pro", "enterprise"]

    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            current_tier = user_tier(request.user)
            if tier_order.index(current_tier) < tier_order.index(min_tier):
                return redirect("upgrade_page")
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def billing_helpers(request):
    return {
        "can_send_messages": can_send_messages,
    }
