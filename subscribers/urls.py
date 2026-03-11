from django.urls import path
from . import views

urlpatterns = [
    path('<int:store_id>/', views.subscriber_list, name='subscriber_list'),
    path('<int:store_id>/add/', views.add_subscriber, name='add_subscriber'),
]
