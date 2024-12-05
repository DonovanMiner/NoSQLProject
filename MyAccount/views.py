from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.core.files.storage import FileSystemStorage  # For handling file uploads
from django.http import JsonResponse
from bson.objectid import ObjectId


from NoSQLProject.utils import users  # , user_fitness_data


# Profile Settings View
def userprofile(request):
<<<<<<< HEAD
    # Retrieve the user_id from session
    # Adjust based on your session key
    user_id = request.session.get("user_id")
    if not user_id:
        return HttpResponse("User is not logged in.", status=401)

    # Fetch user data from MongoDB using user_id
    # Use the appropriate field here
    user = users.find_one({"user_id": user_id})
=======
    # Get the user_id or username from the session
    # Assuming you stored the user_id during login
    user_id = request.session.get("user_id")
    if not user_id:
        # If no user_id in session, the user is not logged in
        return HttpResponse("User is not logged in.", status=401)

    # Fetch user data from MongoDB using the user_id
    user = users.find_one({"_id": ObjectId(user_id)})
>>>>>>> 35f8ad18dbcd569ae6f41d8141cd1b967227524a

    if not user:
        return HttpResponse("User not found.", status=404)

<<<<<<< HEAD
    # Pass user data to the template
=======
    # Pass the user data to the template
>>>>>>> 35f8ad18dbcd569ae6f41d8141cd1b967227524a
    return render(request, 'MyAccount/userprofile.html', {'user': user})


def settings(request):
    username = request.session.get("username")
    if not username:
        # User not logged in
        return HttpResponse("User is not logged in.", status=401)

    user = users.find_one({"username": username})
    if not user:
        # No user found in database
        return HttpResponse("User not found", status=404)

    return render(request, 'MyAccount/userprofile.html', {'user': user})
