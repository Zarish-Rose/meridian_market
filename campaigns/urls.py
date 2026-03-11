from django.urls import path
from . import views

urlpatterns = [
    path('<int:store_id>/', views.campaign_list, name='campaign_list'),
    path('<int:store_id>/create/', views.create_campaign, name='create_campaign'),
]
