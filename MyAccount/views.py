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
    # Retrieve the user_id from session
    user_id = request.session.get("u_id")
    if not user_id:
        return HttpResponse("User is not logged in.", status=401)

    # Fetch user data from MongoDB
    user = users.find_one({"_id": ObjectId(user_id)})

    if not user:
        return HttpResponse("User not found.", status=404)

    # Pass user data to the template
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
