from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader


from NoSQLProject.utils import user_fitness_data #import clinet, db as well?

def home(request):
    
    res = user_fitness_data.find().limit(10)
    context = {'res' : res}

    return HttpResponse(render(request, 'Landing/home.html', context))

