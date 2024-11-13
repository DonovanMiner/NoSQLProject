from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader

from NoSQLProject.utils import user_fitness_data #import clinet, db as well?

# Home page view (before login)
def home(request):
    return render(request, 'landing/home.html')

# workouts page view
def workouts(request):
    workout_data = user_fitness_data.find().limit(10)
    context = {'workout_data': workout_data}
    return render(request, 'landing/workouts.html', context)

# how it works page view
def how_it_works(request):
    return render(request, 'landing/how_it_works.html', context)

# login/sign-up page view
def login_signup(request):
    return render(request, 'landing/login_signup.html', context)

## After login request (dashboard view)
def dashboard(request)
    user_name = request.user.first_name
    progress = {"completed_goals": 3, "total_goals": 5}
    context = {"user_name": user_name, "progress": progress}
    return render(request, 'landing/dashboard/html', context)

def home(request):
    
    res = user_fitness_data.find().limit(10)
    context = {'res' : res}

    return HttpResponse(render(request, 'Landing/home.html', context))
