from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from datetime import datetime
from django.contrib.auth.hashers import make_password, check_password

from NoSQLProject.utils import user_fitness_data, users #import clinet, db as well?

# Home page view (before login)
def home(request):
    res = user_fitness_data.find().limit(10)
    context = {'res' : res}
    return render(request, 'Landing/home.html', context)

# how it works page view
def how_it_works(request):
    context = {} #this will be updated later since it will not use data
    return render(request, 'Landing/how_it_works.html', context)

# Login/Sign-up page view
def login_signup(request):
    # Define the height drop down list options range from 4'0" to 7'11"
    heights = []
    for ft in range(4, 8):  
        for in_ in range(0, 12): 
            heights.append(f"{ft}' {in_:02d}\"")  

    if request.method == "POST":
        action = request.POST.get('action')
        
        # Handling login:
        if action == 'login':
            username = request.POST['username']
            password = request.POST['password']

            # Find the user in the MongoDB collection based on the u_name (username)
            user = users.find_one({'u_name': username})
            
            if user and check_password(password, user['password']):
                request.session['user_id'] = user['user_id']
                return redirect('Dashboard:user_dashboard') 
            else:
                messages.error(request, "Invalid username or password")
                return redirect('Landing:login_signup')
        
        # Handling sign-up:
        elif action == 'signup':
            u_name = request.POST['u_name']
            f_name = request.POST['f_name']
            l_name = request.POST['l_name']
            email_addr = request.POST['email_addr']
            password = request.POST['password']
            gender = request.POST['gender']
            dob = request.POST['dob']
            height = request.POST['height']  
            weight = request.POST['weight']
            
            # Find and assign the next available number for as the user_id for this new_user
            last_user = users.find().sort("user_id", -1).limit(1)
            new_user_id = last_user[0]['user_id'] + 1 if last_user.count() > 0 else 1
            
            # capturing the account creation date
            date_of_creation = datetime.now()

            # Checking up if email already exists in the MongoDB 'users' collection
            existing_user = users.find_one({'email_addr': email_addr})
            if existing_user:
                messages.error(request, "Email already in use")
                return redirect('Landing:login_signup')
            
            #hash the password before saving it - i do not think its necessary, but the best practices do it for production environment
            hashed_password = make_password(password)

            # Create a new user document in MongoDB:
            new_user_data = {
                'user_id': new_user_id,
                'u_name': u_name,
                'f_name': f_name,
                'l_name': l_name,
                'email_addr': email_addr,
                'password': hashed_password,  #Should we consider hashing the passwords??
                'gender': gender,
                'dob': dob,
                'height': height,
                'weight': weight,
                'date_of_creation': date_of_creation, ##shoudl we save the time of creation??
            }

            # Store the new_user_data into the users collection in mongodb
            users.insert_one(new_user_data)
            
            # Log the new user in automatically
            request.session['user_id'] = new_user_data['user_id']

            return redirect('Dashboard:user_dashboard')
    
    return render(request, 'Landing/login_signup.html', {'heights': heights})

##### check this
def dashboard(request):
    user_id = request.session.get('user_id') 
    user = users.find_one({'user_id': user_id})

    if user:
        user_name = user['f_name']
        user_progress = user_fitness_data.find_one({'user_id': user_id}) 
        progress = user_progress.get('progress', {'completed_goals': 0, 'total_goals': 0}) ### check this
        context = {'user_name': user_name, 'progress': progress}
        return render(request, 'Landing/dashboard.html', context)
    else:
        return redirect('Landing:login_signup')  # If no user found, redirect to login
    return render(request, 'Landing/dashboard.html', context)