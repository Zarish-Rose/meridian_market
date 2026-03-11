from django.urls import path
from . import views

urlpatterns = [
    path('<int:store_id>/', views.subscriber_list, name='subscriber_list'),
    path('<int:store_id>/add/', views.add_subscriber, name='add_subscriber'),
    path('<int:store_id>/<int:subscriber_id>/edit/', views.edit_subscriber, name='edit_subscriber'),
    path('<int:store_id>/<int:subscriber_id>/delete/', views.delete_subscriber, name='delete_subscriber'),
]
