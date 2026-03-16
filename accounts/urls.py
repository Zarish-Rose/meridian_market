from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='accounts_index'),

    # Authentication
    path('about/', views.about, name='about'),
    path('login/', auth_views.LoginView.as_view(template_name='home/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('myprofile/', views.my_profile, name='my_profile'),
]
