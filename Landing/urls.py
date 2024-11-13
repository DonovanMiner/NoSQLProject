from django.urls import path
from . import views

app_name = 'Landing'

urlpatterns = [
    path('', views.home, name='home'), 
    path('workouts/', views.workouts, name='workouts'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('login-signup/', views.login_signup, name='login_signup'),
    path('dashboard/', views.dashboard, name='dashboard'),  
]
