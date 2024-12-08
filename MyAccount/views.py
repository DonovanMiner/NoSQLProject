from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from bson.objectid import ObjectId


from NoSQLProject.utils import users, user_fitness_data

# View for displaying the user profile


def userprofile(request):
    # Get the user_id from the session
    user_id = request.session.get('u_id')

    if not user_id:
        return HttpResponse("User is not logged in.", status=401)

    # Retrieve user data from MongoDB using the user_id
    user = users.find_one({'user_id': user_id['user_id']})

    if not user:
        return HttpResponse("User not found.", status=404)

    # Render the profile page with the full user data
    return render(request, 'MyAccount/userprofile.html', {'user': user})


def update_bio(request):
    # Get the user_id from the session
    user_id = request.session.get('u_id')

    # If user_id is not found, return a "User is not logged in" message
    if not user_id:
        return HttpResponse("User is not logged in.", status=401)

    # Retrieve user data from MongoDB using the user_id
    user = users.find_one({'user_id': user_id['user_id']})

    if not user:
        return HttpResponse("User not found.", status=404)

    # Handle POST request to update the bio
    if request.method == 'POST':
        bio = request.POST.get('bio')  # Get the new bio from the form

        # If bio is provided, update the user's bio in MongoDB
        if bio is not None:
            users.update_one(
                {'user_id': user_id['user_id']},
                {'$set': {'bio': bio}}  # Set the bio field in the user's document
            )
            messages.success(request, "Bio updated successfully!")

        # Fetch the updated user data and render the profile page with the new bio
        user = users.find_one({'user_id': user_id['user_id']})
        return render(request, 'MyAccount/userprofile.html', {'user': user})

    return HttpResponse("Invalid request method.", status=400)

def settings(request):
    # Get the user_id from the session
    user_id = request.session.get('u_id')

    if not user_id:
        return HttpResponse("User is not logged in.", status=401)

    # Retrieve user data from MongoDB using the user_id
    user = users.find_one({'user_id': user_id['user_id']})

    if not user:
        return HttpResponse("User not found.", status=404)

    # Pass user data to the template
    return render(request, 'MyAccount/settings.html', {'user_id': user_id['user_id']})


# View to update the user's profile (username and email)


def update_profile(request):
    user_id = request.session.get('u_id')

    if not user_id:
        return HttpResponse("User is not logged in.", status=401)

    user = users.find_one({'user_id': user_id['user_id']})

    if not user:
        return HttpResponse("User not found.", status=404)

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        # Check if the new username/email already exists
        if username:
            existing_user = users.find_one({'u_name': username})
            if existing_user:
                messages.error(request, "Username is already taken.")
            else:
                users.update_one({'user_id': user_id}, {'$set': {'u_name': username}})

        if email:
            existing_user = users.find_one({'email_addr': email})
            if existing_user:
                messages.error(request, "Email is already taken.")
            else:
                users.update_one({'user_id': user_id}, {'$set': {'email_addr': email}})

        messages.success(request, "Profile updated successfully!")
        return redirect('MyAccount:settings')

    return render(request, 'MyAccount/settings.html', {'user_id': user_id['user_id']})

# View to change the user's password


def change_password(request):
    user_id = request.session.get('u_id')

    if not user_id:
        return HttpResponse("User is not logged in.", status=401)

    user = users.find_one({'user_id': user_id['user_id']})

    if not user:
        return HttpResponse("User not found.", status=404)

    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Check if old password matches the current password
        if old_password != user['password']:
            return HttpResponse("Old password is incorrect.", status=400)

        # Check password confirmation
        if new_password and new_password == confirm_password:
            # Update the password with the new value
            users.update_one({'user_id': user_id}, {'$set': {'password': new_password}})
            messages.success(request, "Password updated successfully!")
        else:
            if new_password != confirm_password:
                return HttpResponse("Passwords do not match.", status=400)

        # Redirect back to the settings page
        return redirect('MyAccount:settings')

    return render(request, 'MyAccount/change_password.html')

# View to delete the user's account


def delete_account(request):
    user_id = request.session.get('u_id')

    if not user_id:
        return HttpResponse("User is not logged in.", status=401)

    if request.method == 'POST':
        delete_username = request.POST.get('delete_username')
        delete_password = request.POST.get('delete_password')

        user = users.find_one({'user_id': user_id['user_id']})

        if not user:
            return HttpResponse("User not found.", status=404)

        # Check if the username and password match for confirmation
        if delete_username != user['u_name'] or delete_password != user['password']:
            return HttpResponse("Username or password is incorrect.", status=400)

        # Delete the user's related fitness data and the user document
        user_fitness_data.delete_many({'user_id': user_id['user_id']})
        users.delete_one({'user_id': user_id['user_id']})  

        # Optionally log the user out after deletion
        request.session.flush()  # Clear session data

        # Redirect to the home page or a confirmation page
        return redirect('Landing:home')

    return HttpResponse("Invalid request method.", status=400)
