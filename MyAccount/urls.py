
from django.urls import path
from . import views  

app_name = 'MyAccount'  

urlpatterns = [
    path('', views.profile_settings, name='profile_settings'),
    path('change-profile-photo/', views.change_profile_photo, name='change_profile_photo'),
    path('change-password/', views.change_password, name='change_password'),
    path('change-bio/', views.change_bio, name='change_bio'),
    path('change-username/', views.change_username, name='change_username'),
    path('change-password/', views.change_password, name='change_password'),
    path('change-bio/', views.change_bio, name='change_bio'),
    path('delete_profile_photo/', views.delete_profile_photo, name='delete_profile_photo'),
]