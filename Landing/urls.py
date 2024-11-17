from django.urls import path
from . import views

app_name = 'Landing'

urlpatterns = [
    path('', views.home, name='home'), 
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('login-signup/', views.login_signup, name='login_signup'),
]