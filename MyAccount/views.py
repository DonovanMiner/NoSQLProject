from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.hashers import make_password, check_password #idk if this is necessary tbh, i hashed the password in login
from django.core.files.storage import FileSystemStorage

from NoSQLProject.utils import user_fitness_data, users

# Create your views here.

def profile_settings(request):
    return render(request, 'profile_settings.html')

def progress(request):
    return render(request, 'progress.html')

def preferences(request):
    return render(request, 'preferences.html')
