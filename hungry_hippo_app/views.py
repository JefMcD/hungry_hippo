
# Standard
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404

# Authentication
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Database
from django.db import IntegrityError
from .models import *

# File Handling
from django.core.files.storage import default_storage
from django.core.exceptions import SuspiciousFileOperation
import os

# Forms
from django.views.decorators.csrf import csrf_exempt
from .forms import *

# Image Handling
from PIL import Image
from django.core.files import File
from django.core.files.images import ImageFile


# There are a lot of Django Queries here
# https://docs.djangoproject.com/en/dev/topics/db/queries/


def entry(request):
    # If user is authenticated load profile
    if request.user.is_authenticated:
        current_user = User.objects.get(pk = request.user.id)
        print(f"############# current user => {current_user}")
        user_profile = User_Profile.objects.get(user_id_fk = current_user)
        profile_id = user_profile.user_profile_id
        user_name = current_user.username
        return HttpResponseRedirect(reverse("hungry_hippo_app:index"))
    else:
        # load authentication options
        return render(request, "hungry_hippo_app/authenticate_options.html")


def register(request):
    print(f"#### register ####")      
        
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        
        #Django validation checks username is unique

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        
        if password != confirmation:    
            return render(request, "hungry_hippo_app/register.html", {
                "message": "Passwords must match."
            })
            
        # Check if email address is already in use
        email_address_is_taken = User.objects.filter(email = request.POST['email'])
        if email_address_is_taken:
                context_dictionary = {"message": "email already being used."}
                return render(request, "hungry_hippo_app/register.html", context_dictionary)
            
        # TODO Confirm and Validate Registration by email/phone

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()

        except IntegrityError:
            # remove the user profile directory area
            return render(request, "hungry_hippo_app/register.html", {
                "message": "Username already taken."
            })
            
        login(request, user)
        create_user_profile(request)
        return HttpResponseRedirect(reverse('hungry_hippo_app:index'))
    else:
        return render(request, "hungry_hippo_app/register.html")
    
    
def create_user_profile(request):
    print (f"#### create_user_profile ####")
    
    # Define filesystem directory tree for the users uploads
    # At this point The user has been entered in the User table and has been logged in
    current_user = User.objects.get(pk = request.user.id)
    username = current_user.username   
       
    # its also important to remember where you have defined MEDIA_ROOT and MEDIA_URL for user uploads
    # MEDIA_ROOT is where the app will upload files
    # MEDIA_URL is the root url realtive to the project root directory. This is where it will look for files when you give it a pathname such as a username
    media_root = settings.MEDIA_ROOT
    media_url  = settings.MEDIA_URL
    print(f"MEDIA_ROOT => {media_root}") # /home/artillery/webdev-apps/courses/CS50/Project-4/hungry_hippo_app/user_profiles
    print(f"MEDIA_URL => {media_url}")   # /user_profiles/     
       
    # Create an instance in the User_Profile table and assign defaults where necessary
    try:
        
        folder = os.path.join(media_url,username)
        print(f"user folder => {folder}")
        new_user_profile = User_Profile(user_id_fk = current_user,
                                        user_profile_folder = folder)
        new_user_profile.save()
            
    except IntegrityError:
        # delete the user profile directory area
        # delete User
        return render(request, "hungry_hippo_app/register.html", {
            "message": "Error creating User Profile.",
        })
        
    return
    

 
    
def page_404(request, message):
    pass
    

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            current_user = User.objects.get(pk = request.user.id)
            return HttpResponseRedirect(reverse("hungry_hippo_app:index"))
        else:
            return render(request, "hungry_hippo_app/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "hungry_hippo_app/login.html")


def logout_view(request):
    # Delete all the processing data associated with the user
    print(f"Deleting User Data")
    current_user = User.objects.get(pk = request.user.id)
    user_profile = User_Profile.objects.get(user_id_fk = current_user)
    
    user_image_sets = Image_Set.objects.filter(user_profile_id_fk = user_profile.pk)
    for image_set in user_image_sets:
        image_set.delete()
        
    print(f"Logging Out")
    
    logout(request)
    print(f"Redirect")
    return HttpResponseRedirect(reverse("hungry_hippo_app:entry"))


@login_required
def index(request):
    tag_form = Tag_Upload_Form()
    source_folder_form = Source_Folder_Form()
    action_set_image_widths = Action_Set_Image_Widths()
    action_set_image_heights = Action_Set_Image_Heights() 
    tag_placement = Tag_Position_Form()
    
    
    image_url = os.path.join(settings.MEDIA_URL,'hippo1.jpg')
    return render(request, "hungry_hippo_app/index.html", {
                    'debug_message': 'CropperJS Debug',
                    'work_image': image_url,
                    'tag_form': tag_form,
                    'source_folder_form': source_folder_form,
                    'action_set_image_widths': action_set_image_widths,
                    'action_set_image_heights': action_set_image_heights,  
                    'tag_placement': tag_placement                 
    })
























