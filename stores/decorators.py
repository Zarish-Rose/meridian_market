from django.core.exceptions import PermissionDenied
from .models import Store, StoreMember

def store_access_required(view_func):
    def wrapper(request, store_id, *args, **kwargs):
        user = request.user

        # Admins always allowed
        if user.profile.role == 'admin':
            return view_func(request, store_id, *args, **kwargs)

        # Check if store exists
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            raise PermissionDenied

        # Owners always allowed for their own stores
        if store.owner == user:
            return view_func(request, store_id, *args, **kwargs)

        # Staff: check membership
        is_member = StoreMember.objects.filter(store=store, user=user).exists()
        if is_member:
            return view_func(request, store_id, *args, **kwargs)

        # Otherwise: forbidden
        raise PermissionDenied

    return wrapper
