
from django.urls import path
from . import views

app_name = 'MyAccount'

urlpatterns = [
    path('', views.userprofile, name='userprofile'),
    path('settings/', views.settings, name='settings'),
]
