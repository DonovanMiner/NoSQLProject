from django.urls import path
from . import views

app_name = "Dashboard"
urlpatterns = [

    path('', views.default_dashboard, name='default_dash'),
    path('user/', views.user_dashboard, name='user_dash'),
    path('user/update/', views.update_user_dashboard, name='update_user_dash'),
    path('user/update-workout/', views.update_workout, name='update_workout'),
    path('user/edit-workout/', views.edit_workout, name='edit_workout'),
    path('user/create-workout/', views.create_workout, name='create_workout'),

]
