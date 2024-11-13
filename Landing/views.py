from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader

from NoSQLProject.utils import user_fitness_data #import clinet, db as well?

# Home page view (before login)
def home(request):
    res = user_fitness_data.find().limit(10)
    context = {'res' : res}
    return HttpResponse(render(request, 'Landing/home.html', context))

# workouts page view
def workouts(request):
    workout_data = user_fitness_data.find().limit(10)
    context = {'workout_data': workout_data}
    return HttpResponse(render(request, 'landing/workouts.html', context)

# how it works page view
def how_it_works(request):
    context = {} #going to be defined later since it will not use data
    return HttpResponse(render(request, 'landing/how_it_works.html', context)

# login/sign-up page view
def login_signup(request):
    context = {} #this will be empty until we find out how to authenticate users and stuff.
    return HttpResponse(render(request, 'landing/login_signup.html', context)

## After login request (dashboard view)
def dashboard(request):
    user_name = request.user.first_name
    progress = {"completed_goals": 3, "total_goals": 5}
    context = {"user_name": user_name, "progress": progress}
    return HttpResponse(render(request, 'landing/dashboard.html', context)
