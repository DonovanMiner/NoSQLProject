from django.urls import path
from . import views

app_name = 'MyAccount'

urlpatterns = [
    path('', views.userprofile, name='userprofile'),
    path('settings/', views.settings, name='settings'),
    path('update_bio/', views.update_bio, name='update_bio'),
    # For updating username and email
    path('update_profile/', views.update_profile, name='update_profile'),
    path('change_password/', views.change_password,
         name='change_password'),  # For changing the password
    path('delete_account/', views.delete_account,
         name='delete_account'),  # For deleting the account
]
