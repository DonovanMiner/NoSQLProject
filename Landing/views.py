from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import authenticate, login #ask Donovan if he could fix the user authentication problem with the database in MongoDB
from django.contrib.auth.models import User
from django.contrib import messages 


from NoSQLProject.utils import user_fitness_data #import clinet, db as well?

# Home page view (before login)
def home(request):
    res = user_fitness_data.find().limit(10)
    context = {'res' : res}
    return render(request, 'Landing/home.html', context)

# how it works page view
def how_it_works(request):
    context = {} #this will be defined later since it will not use data
    return render(request, 'Landing/how_it_works.html', context)

# login/sign-up page view
def login_signup(request):
    if request.method == "POST":
        action = request.POST.get('action')  #this is for login or sigunp
        
        #Handling login:
        if action == 'login':
            username = request.POST['username']
            password = request.POST['password']
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('Dashboard:user_dashboard') # Redirect to dashboard after login
            else:
                messages.error(request, "Invalid username or password")
                return redirect('Landing:login_signup')
        
        #Handling sign-up
        elif action == 'signup':
            new_username = request.POST['new_username']
            new_password = request.POST['new_password']
            
            #Check if username exists in the db:
            if User.objects.filter(username=new_username).exists():
                messages.error(request, "Username already taken")
                return redirect('Landing:login_signup')
            
            #create a new user:
            user = User.objects.create_user(username=new_username, password=new_password)
            user.save()
            
            #redirect new user to dashboard mainpage (log immediately)
            login(request, user)
            return redirect('Dashboard:user_dashboard')
    
    return render(request, 'Landing/login_signup.html')

#After login request (dashboard view)
# Needs to be configured with the actual attributes of the database related to the users collection.
def dashboard(request):
    user_name = request.user.first_name
    user_progress = user_fitness_data.find_one({'user_id':request.user.id}) #adjust query according to our actual database.
    progress = user_progress.get('progress', {'completed_goals': 0, 'total_goals': 0})
    context = {'user_name':user_name, 'progress': progress}  #Edit when we find out how to authenticate users and stuff.
    return render(request, 'Landing/dashboard.html', context)