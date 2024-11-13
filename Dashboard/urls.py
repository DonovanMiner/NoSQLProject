from django.urls import path
from . import views

app_name = "Dashboard"
urlpatterns = [
    
    path('', views.default_dashboard, name='default_dash'),
    path('user/', views.user_dashboard, name='user_dash'),
    
    ]