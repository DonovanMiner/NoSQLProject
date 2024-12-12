from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from bson.objectid import ObjectId
from bson import Binary



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
            messages.success(request, "Bio updated successfully.", extra_tags='bio')

        # Fetch the updated user data and render the profile page with the new bio
        user = users.find_one({'user_id': user_id['user_id']})
        return render(request, 'MyAccount/userprofile.html', {'user': user})

    return HttpResponse("Invalid request method.", status=400)

def update_username(request):
    # Get the user_id from the session
    user_id = request.session.get('u_id')

    # If user_id is not found, return a "User is not logged in" message
    if not user_id:
        return HttpResponse("User is not logged in.", status=401)

    # Retrieve user data from MongoDB using the user_id
    user = users.find_one({'user_id': user_id['user_id']})

    if not user:
        return HttpResponse("User not found.", status=404)

    # Handle POST request to update the username
    if request.method == 'POST':
        new_username = request.POST.get('new_username')  # Get the new username from the form

        # Check if new_username is provided
        if new_username:
            # Ensure the new username is not the same as the current username
            if new_username == user['u_name']:
                messages.error(request, "Username already exists. Please choose a different username.", extra_tags='username_error')
            else:
                # Check if the new username already exists in the database
                existing_user = users.find_one({'u_name': new_username})
                if existing_user:
                    messages.error(request, "Username not available. try with a different username.", extra_tags='username_error')
                else:
                    # Update the user's username in MongoDB
                    users.update_one(
                        {'user_id': user_id['user_id']},
                        {'$set': {'u_name': new_username}}  # Set the username field in the user's document
                    )
                    messages.success(request, "Username updated successfully.", extra_tags='username')

        # Fetch the updated user data and render the profile page with the new username
        user = users.find_one({'user_id': user_id['user_id']})
        return render(request, 'MyAccount/userprofile.html', {'user': user})

    return HttpResponse("Invalid request method.", status=400)

def verify_current_password(request):
    # Get the user_id from the session
    user_id = request.session.get('u_id')

    if not user_id:
        return HttpResponse("User is not logged in.", status=401)

    # Retrieve user data from MongoDB using the user_id
    user = users.find_one({'user_id': user_id['user_id']})

    if not user:
        return HttpResponse("User not found.", status=404)

    if request.method == 'POST':
        current_password = request.POST.get('current_password')

        # Check if the entered current password matches the stored password
        if current_password != user['password']:
            messages.error(request, "Current password is incorrect.", extra_tags='password')
            return render(request, 'MyAccount/userprofile.html', {'user': user})

        # If correct, show the new password form
        return render(request, 'MyAccount/userprofile.html', {'update_password': True, 'user': user})

    return HttpResponse("Invalid request method.", status=400)


def update_password(request):
    # Get the user_id from the session
    user_id = request.session.get('u_id')

    if not user_id:
        return HttpResponse("User is not logged in.", status=401)

    # Retrieve user data from MongoDB using the user_id
    user = users.find_one({'user_id': user_id['user_id']})

    if not user:
        return HttpResponse("User not found.", status=404)

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')

        # Check if new password and confirmation match
        if new_password != confirm_new_password:
            messages.error(request, "New passwords do not match.", extra_tags='password_error')
            return render(request, 'MyAccount/userprofile.html', {'user': user})

        # Check if new password is different from the current one
        if new_password == user['password']:
            messages.error(request, "New password cannot be the same as the current password.", extra_tags='password_error')
            return render(request, 'MyAccount/userprofile.html', {'user': user})

        # Update the password in the database
        users.update_one(
            {'user_id': user_id['user_id']},
            {'$set': {'password': new_password}}
        )

        messages.success(request, "Password updated successfully.", extra_tags='password')
        return redirect('MyAccount:userprofile')

    return HttpResponse("Invalid request method.", status=400)