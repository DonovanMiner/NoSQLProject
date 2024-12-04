from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.hashers import check_password

from NoSQLProject.utils import user_fitness_data, users

# Home page view (before login)


def home(request):
    res = user_fitness_data.find().limit(10)
    context = {'res': res}
    return render(request, 'Landing/home.html', context)

# how it works page view


def how_it_works(request):
    context = {}  # this will be updated later since it will not use data
    return render(request, 'Landing/how_it_works.html', context)

# Login/Sign-up page view


def login_signup(request):
    print("Here 1")
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
                # Redirect to user_dashboard after login
                return redirect('Dashboard:user_dash')
            else:
                messages.error(request, "Invalid username or password")
                return redirect('Landing:login_signup')

        # Handling sign-up:
        elif action == 'signup':
            print("Here 2")
            username = request.POST['username']
            f_name = request.POST['f_name']
            l_name = request.POST['l_name']
            email_addr = request.POST['email_addr']
            password = request.POST['password']
            gender = request.POST['gender']
            dob = request.POST['dob']
            height = request.POST['height']
            weight = request.POST['weight']

            # Find and assign the next available number for as the user_id for this new_user
            last_user = users.find_one(sort=[("user_id", -1)])
            new_user_id = last_user['user_id'] + 1 if last_user else 1

            # capturing the account creation date
            date_of_creation = datetime.now()

            # Checking if email already exists in the MongoDB 'users' collection
            existing_user = users.find_one({'email_addr': email_addr})
            if existing_user:
                messages.error(request, "Email already in use")
                return redirect('Landing:login_signup')

            # Create a new user document in MongoDB:
            new_user_data = {
                'user_id': new_user_id,
                'u_name': username,
                'f_name': f_name,
                'l_name': l_name,
                'email_addr': email_addr,
                'password': password,
                'gender': gender,
                'dob': dob,
                'height': height,
                'weight': weight,
                'date_of_creation': date_of_creation,
            }

            # Store the new_user_data into the users collection in MongoDB
            users.insert_one(new_user_data)

            # Fetch the user to set the session
            user = users.find_one({'u_name': username})

            if user:
                request.session['u_name'] = username
                request.session['u_id'] = new_user_id
                print("Redirecting to Dashboard")
                # Redirect to the user_dashboard after successful signup
                return redirect('Dashboard:user_dash')

            else:
                # If the user isn't found, show an error message
                messages.error(request, "Something went wrong during sign-up.")
                return redirect('Landing:login_signup')

    return render(request, 'Landing/login_signup.html', {'heights': heights})
