from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile_settings, name='profile_settings'),
    path('progress/', views.progress, name='progress'),
    path('preferences/', views.preferences, name='preferences'),
]