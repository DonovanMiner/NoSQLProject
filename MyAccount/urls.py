from django.urls import path
from . import views

app_name = 'MyAccount'

urlpatterns = [
    path('', views.userprofile, name='userprofile'),
    path('update_bio/', views.update_bio, name='update_bio'),
    path('update_username/', views.update_username, name='update_username'),
    path('verify_current_password/', views.verify_current_password, name='verify_current_password'),
    path('update_password/', views.update_password, name='update_password'),
]
