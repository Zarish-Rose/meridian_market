from django.urls import path
from . import views

urlpatterns = [
    path('', views.store_list, name='store_list'),
    path('create/', views.create_store, name='create_store'),
]
