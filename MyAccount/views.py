from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.core.files.storage import FileSystemStorage  # For handling file uploads
from django.http import JsonResponse
from bson.objectid import ObjectId


from NoSQLProject.utils import users, user_fitness_data


# Profile Settings View
def profile_settings(request):
    username = request.session.get("username")
    if not username:
        return HttpResponse("User is not logged in.", status=401)  # User not logged in

    user = users.find_one({"username": username})
    if not user:
        return HttpResponse("User not found", status=404)  # No user found in database

    return render(request, 'MyAccount/profile_settings.html', {'user': user})

def change_profile_photo(request):
    username = request.session.get("username")
    if not username:
        return HttpResponse("User is not logged in.", status=401)  # User not logged in

    user = users.find_one({"username": username})
    if not user:
        return HttpResponse("User not found", status=404)  # No user found in database

    if request.method == 'POST':
        new_photo = request.FILES.get('new_photo')
        if new_photo:
            # Save the uploaded file locally
            fs = FileSystemStorage()
            filename = fs.save(new_photo.name, new_photo)
            file_url = fs.url(filename)

            # Update user's photo URL in MongoDB
            users.update_one({"_id": user["_id"]}, {"$set": {"photo": file_url}})
            messages.success(request, "Profile photo updated successfully.")
        else:
            messages.error(request, "No photo was uploaded.")
        return redirect('MyAccount:profile_settings')

    return HttpResponse("Invalid request method.", status=405)

# Change Bio View
def change_bio(request):
    username = request.session.get("username")
    if not username:
        return HttpResponse("User is not logged in.", status=401)  # User not logged in

    user = users.find_one({"username": username})
    if not user:
        return HttpResponse("User not found", status=404)  # No user found in database

    if request.method == 'POST':
        new_bio = request.POST.get('new_bio')
        if new_bio:
            # Update the user's bio in MongoDB
            users.update_one({"_id": user["_id"]}, {"$set": {"bio": new_bio}})
            messages.success(request, "Bio updated successfully.")
        else:
            messages.error(request, "No bio provided.")

        return redirect('MyAccount:profile_settings')  # Redirect to profile settings after updating the bio

    return HttpResponse("Invalid request method.", status=405)

# Change Username View
def change_username(request):
    username = request.session.get("username")
    if not username:
        return HttpResponse("User is not logged in.", status=401)  # User not logged in

    user = users.find_one({"username": username})
    if not user:
        return HttpResponse("User not found", status=404)  # No user found in database

    if request.method == 'POST':
        new_username = request.POST.get('new_username')
        if new_username:
            # Update the user's username in MongoDB
            users.update_one({"_id": user["_id"]}, {"$set": {"username": new_username}})
            messages.success(request, "Username updated successfully.")
        else:
            messages.error(request, "No username provided.")

        return redirect('MyAccount:profile_settings')  # Redirect to profile settings after updating the username

    return HttpResponse("Invalid request method.", status=405)

# Change Password View
def change_password(request):
    username = request.session.get("username")
    if not username:
        return HttpResponse("User is not logged in.", status=401)  # User not logged in

    user = users.find_one({"username": username})
    if not user:
        return HttpResponse("User not found", status=404)  # No user found in database

    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Check if the old password matches the stored one
        if not check_password(old_password, user.get('password')):
            messages.error(request, "Old password is incorrect.")
            return redirect('MyAccount:profile_settings')  # Redirect back to profile settings

        # Check if new password and confirm password match
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect('MyAccount:profile_settings')  # Redirect back to profile settings

        # Hash the new password
        hashed_password = make_password(new_password)

        # Update the user's password in MongoDB
        users.update_one({"_id": user["_id"]}, {"$set": {"password": hashed_password}})

        messages.success(request, "Password changed successfully.")
        return redirect('MyAccount:profile_settings')  # Redirect to profile settings after updating password

    return HttpResponse("Invalid request method.", status=405)

# Delete Profile Photo View
def delete_profile_photo(request):
    username = request.session.get("username")
    if not username:
        return HttpResponse("User is not logged in.", status=401)  # User not logged in

    user = users.find_one({"username": username})
    if not user:
        return HttpResponse("User not found", status=404)  # No user found in database

    if request.method == 'POST':
        # Remove the photo URL from the user's document in MongoDB
        users.update_one({"_id": user["_id"]}, {"$unset": {"photo": ""}})  # This removes the photo field from the document
        messages.success(request, "Profile photo deleted successfully.")
        return redirect('MyAccount:profile_settings')  # Redirect back to profile settings

    return HttpResponse("Invalid request method.", status=405)
