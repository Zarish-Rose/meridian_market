from django.urls import path
from . import views

urlpatterns = [
    path('', views.store_list, name='store_list'),
    path('create/', views.create_store, name='create_store'),
    path('<int:store_id>/', views.store_detail, name='store_detail'),
    path('<int:store_id>/edit/', views.edit_store, name='edit_store'),
    path('<int:store_id>/delete/', views.delete_store, name='delete_store'),
]
