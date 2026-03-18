from django.shortcuts import render, get_object_or_404
from stores.models import Store


def subscribe_page(request, store_slug):
    store = get_object_or_404(Store, slug=store_slug)
    return render(
        request,
        "subscriptions/subscribe_page.html",
        {"store": store},
    )
