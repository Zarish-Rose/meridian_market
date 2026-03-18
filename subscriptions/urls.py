from django.urls import path
from . import views

urlpatterns = [
    path(
        "subscribe/<slug:store_slug>/",
        views.subscribe_page,
        name="subscribe_page",
    ),
]
