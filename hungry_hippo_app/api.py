

# Standard
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.urls import reverse
import re

# Authentication
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Database
from datetime import datetime
from django.db import IntegrityError, DatabaseError
from .models import *

# Javascript API
import json
from django.http import JsonResponse

# File Handling
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import SuspiciousFileOperation
import os
import tempfile
from zipfile import ZipFile

# Forms
from django.views.decorators.csrf import csrf_exempt
from .forms import *

# Image Handling
from PIL import Image, ImageColor
from io import BytesIO
import rawpy
import numpy as np

from django.core.files import File
from django.core.files.images import ImageFile

    
def is_an_image(filename):
    # Here I'm using a with statement to open the image using Image.open() 
    # directly from the file's content, and it will automatically close the file when the 
    # block is exited. This is important for handling resources properly
    
    # BytesIO is a class in the io module that provides an in-memory binary stream. 
    # It allows you to treat a block of bytes as a file-like object, which can be useful 
    # in various scenarios, such as working with libraries that expect file-like input,
    # like the Image.open() method from the Pillow library.

    # Here BytesIO is used to create a file-like object from the content of the uploaded file (image). 
    # This allows the Image.open() method to read the image data directly from memory 
    # rather than from a physical file on the disk.
 
 
    print(f"verifying {filename}")
    try:
        print(f"Try ...................... ")
        # try to open that image and load the data
        with Image.open(BytesIO(filename.read())) as img:
            print(f"image {filename} opened")

        return True
    except Exception as e:
        print(f"file {filename} is not an image. Error {e}")
        return False   

    


@csrf_exempt
@login_required
def upload_images_folder(request):
    print("#### API: upload folder ####")
    
    # Check Request Method is POST
    if request.method != 'POST':
        return JsonResponse({"error": "FormData requires POST request method"}, status = 301)
    
    # get user details
    current_user = request.user
    
    # check user profile exists
    profile_exists = User_Profile.objects.filter(user_id_fk = current_user)
    
    if profile_exists:
        user_profile = User_Profile.objects.get(user_id_fk = current_user)
    else:
        return JsonResponse({"error": "User Profile does Not exist"}, status=404)
    
    
    # If image set already exists, delete it. There Can Be Only One!
    '''
     /* Select all the image sets for the user with username = artVoo */
        SELECT U.username, IMS.image_set_id
        FROM hungry_hippo_app_image_set AS IMS, hungry_hippo_app_user_profile AS UP, hungry_hippo_app_user AS U
        WHERE   U.id = UP.user_id_fk AND
                IMS.user_profile_id_fk = UP.user_profile_id AND
                U.username = 'artVoo';
        
        this roughly translates (the django/python query doesnt return values, just its existance) to
        Image_Set.objects.filter(user_profile_id_fk__user_id_fk__username = current_user.username).exists()
    '''
    image_set_exists = Image_Set.objects.filter(user_profile_id_fk__user_id_fk__username = current_user.username).exists()
    if image_set_exists:
        # delete the image set
        Image_Set.objects.get(user_profile_id_fk__user_id_fk__username = current_user.username).delete()
        
    # create a new Image_Set
    new_image_set = Image_Set(user_profile_id_fk = user_profile)
    new_image_set.save()
    
    raw_formats = ['NEF', 'CR2', 'ARW', 'DNG']  # Add more if needed
    # Iterate through the images in request.FILES and add a new instance to Upload_Files
    for image in request.FILES.getlist('source_images'):
        image_is_valid = is_an_image(image)
        if(image_is_valid):                
            image_instance = Upload_File(image_set_id_fk = new_image_set, image_file = image)
            image_instance.save()
        else:
            # ignore it
            pass

    # If upload contains no valid images return 404        
    upload_files_exist = Upload_File.objects.filter(image_set_id_fk = new_image_set).exists()
    if not upload_files_exist:
        upload_response = {
            'image_file': '',
            'image_set_id': 'No Images',
            'baseimage_id': '',
            'baseimage_name': 'No Image'
        }
        return JsonResponse(upload_response, status=404)
    
    # else return the upload data
    # Create Json Response data
    # The response object contains the first image of the files in the image set and the image_set_id
    first_image = Upload_File.objects.filter(image_set_id_fk = new_image_set).first()
    first_image.baseimage = True
    first_image.save()
    
    image_url = first_image.image_file.url
    image_set_id = new_image_set.pk
    
    baseimage_name = get_shortname(first_image.image_file.name)
    
    upload_response = {
        'image_file': image_url,
        'image_set_id': image_set_id,
        'baseimage_id': first_image.pk,
        'baseimage_name': baseimage_name
    }
    
    return JsonResponse(upload_response, status=201)









@csrf_exempt
@login_required 
def upload_tag(request, user_image_set):
    ## This allows a user to Choose a single image on their local computer and then upload it to the server
    
    # get user details
    current_user = request.user.id
    
    # check user profile exists
    profile_exists = User_Profile.objects.filter(user_profile_id = current_user)
    
    if profile_exists:
        user_profile = User_Profile.objects.get(user_id_fk = current_user)
    else:
        return JsonResponse({"error": "User Profile does Not exist"}, status=404)
    
    
    # Check If user_image_set is valid
    image_set_exists = Image_Set.objects.filter(image_set_id = user_image_set).exists()
    if image_set_exists:
        # retrieve
        image_set = Image_Set.objects.get(image_set_id = user_image_set)
    else:
        return JsonResponse({"error":"Image Set Not Found"}, status=404)

    
    # Create Upload_file instance associated with the Image_Set
    image_tag = request.FILES.get('tag_upload')
    print(f"image_tag => {image_tag}")
    new_tag = Imagetag(image_set_id_fk = image_set,
                            tag = image_tag)
    new_tag.save()
    
    
    # Return the Url of the file on the server to the Javascript Client
    
    # iterate throgh the images in the FILES
    # Create an Instance of Image_Files for each image in the Image_Set

    django_tag_name = new_tag.tag.name
    django_tag_path = "Full (V.long) abs path to the file.. .jpg"
    django_tag_url = new_tag.tag.url
    tagname = get_shortname(new_tag.tag.name)
    
    # 

    return JsonResponse({
            "message":"Tag successfully uploaded", 
            "tagname": tagname,
            "django_tag_url"  : django_tag_url}, status=201)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
 
def render_browse_images_form(request, user_image_set):
    print("API: render_browse_images_form()")
    
    username = request.user.username
    print(f"username = {username}")
    # Retrieve Image_Set
    image_set_instance = Image_Set.objects.get(image_set_id = user_image_set)

    # Retrieve Images
    uploaded_images = Upload_File.objects.filter(image_set_id_fk = image_set_instance)
    
    # Render the images in the Browser_Images template
    context = {
        "images": uploaded_images,
    }
    html_binary = render(request, 'hungry_hippo_app/browse_images_gallery.html', context).content
    
    # Decode returned Binary into html text
    html_images_gallery = html_binary.decode()
    
    return html_images_gallery




@csrf_exempt
@login_required
def get_browse_images(request, user_image_set):
    print(f"API: get_browse_images()")
    
    ## Verify request method
    if(request.method != 'GET'):
        return JsonResponse({"error":"Bad request. GET method expected"}, status=301)
    
    ## Verify User Profile exists
    current_user = User.objects.get(id = request.user.id)
    user_profile_exists = User_Profile.objects.filter(user_id_fk = current_user).exists()
    if user_profile_exists:
       user_profile =  User_Profile.objects.get(user_id_fk = current_user)
    else:
        return JsonResponse({"error: User Profile Does not exist"}, status=404)
    
    images_form = render_browse_images_form(request, user_image_set)
    
    return JsonResponse({"images_html": images_form}, status=201)
    
    



# Resize image to a new size
# Longest size is resized to new size with the other side resized proportionately

def resize_image(image_file, size='max'):
    print(f"API: resize_image: {size}")
    
    width, height = image_file.size
    # PIL resize takes a tuple (width, height) as first parameter
    # Determine the longest side and then resize to the requested dimensions keeping apect ratio
    if width > height:
        new_width = size
        new_height =  round((height/width) * size)
    else:
        new_height = size
        new_width = round((width/height) * size)
    
    print(f"Image_File: width = {width}: height = {height}")
    print("Resizing")
    resized_image = image_file.resize((new_width, new_height))
    print("Resized. printing dimensions")
    resize_width, resize_height = resized_image.size
    print(f"resized_image: width = {resize_width}: height = {resize_height}")
    
    return resized_image

  
  
  
def squarify_image(image_file):
    # Returns a PIL Image in a Square Canvas with a plain white background
    print("API: Squarify Image")
    
    # Get Image file dimensions
    width, height = image_file.size
    
    # create a blank square canvas to paste the image_file into
    if width > height:
        # landscape format so margin top and bottom
        square_canvas = Image.new('RGB', (width, width), ImageColor.getrgb('white'))
        
        # calculate where the pasted image should be to center it
        margin = round((width - height)/2)
        x_offset = 0
        y_offset = margin
    else:
        # Portrait format so margin left and right
        square_canvas = Image.new('RGB', (height, height), ImageColor.getrgb('white'))
        
        # calculate where the pasted image should be to center it
        margin = round((height - width)/2)
        x_offset = margin
        y_offset = 0

    print("Aquare canvas created")
    print(f"image_file: height = {height}: width = {width}")
    
    # place image_file in the middle of the new canvas
    square_canvas.paste(image_file, (x_offset, y_offset))

    
    return square_canvas


  
    

def get_imagename(image_filename):
    #  return the filenmae from the image_filename ie '/path/myfile.jpg' returns 'myfile'
    pattern = r'[^\/]+(?=\.\w+$)'

    match = re.search(pattern, image_filename)
    if match:
        filename = match.group()

    return filename


def get_shortname(image_filename):
    #  return the filenmae from the image_filename ie '/path/myfile.jpg' returns 'myfile'
    # IT DOESNT RETURN THE FORWARD SLASH. The forward slash causes path traversal errors
    pattern = r'([^/]+)$'

    match = re.search(pattern, image_filename)
    if match:
        filename = match.group()

    return filename

def process_cropper_data(cropper_data, image_set):
    
    # Retrieve the PIL_Cropper instance for this Image_Set, or Create one if it doesnt exist
    pil_cropper_set_exists = PIL_Cropper.objects.filter(image_set_id_fk = image_set).exists()
    if pil_cropper_set_exists:
        pil_cropper_set = PIL_Cropper.objects.get(image_set_id_fk = image_set)
    else:
        pil_cropper_set = PIL_Cropper(image_set_id_fk = image_set)
    # Extract Cropper data to calculate PIL dimensions
    crop_x_offset = int(cropper_data["crop_x_offset"])
    crop_y_offset = int(cropper_data["crop_y_offset"])
    crop_width    = int(cropper_data["crop_width"])
    crop_height   = int(cropper_data["crop_height"])
    crop_scale_x  = int(cropper_data["crop_scale_x"])
    crop_scale_y  = int(cropper_data["crop_scale_y"]) 
    
    # PIL Co-ordinates. image origin is 0,0 left upper corner
    # crop parameter is a tuple. (left, upper, right, lower) or (x1, y1, x2, y2)
    pil_cropper_set.pil_crop_left   = crop_x_offset
    pil_cropper_set.pil_crop_upper  = crop_y_offset
    pil_cropper_set.pil_crop_right  = crop_x_offset + crop_width
    pil_cropper_set.pil_crop_lower  = crop_y_offset + crop_height
    pil_cropper_set.pil_crop_width  = crop_width
    pil_cropper_set.pil_crop_height = crop_height
    pil_cropper_set.pil_scale_x     = crop_scale_x
    pil_cropper_set.pil_scale_y     = crop_scale_y

    # Get Cropper rotation
    pil_cropper_set.pil_rotation = int(cropper_data["image_rotation"]) * int(-1)
    
    # Pillow rotation is 0 -> 360 moving counter-clockwise or or 0 -> -360 moving clockwise 
    # However, the User interface rotation slider is centered on 0 between -180 and 180, 
    # Fortunatley PIL does negative rotations so the the rotation is converted to PIL format by simply multiplying by -1
    # image_rotation = image_rotation * int(-1)
    
    pil_cropper_set.save()

    return


def process_action_set_data(action_set_data, image_set):
    print(f"API: process_action_set_data")
    
    # Retrieve the Action_Set for this Image_Set, or Create one if it doesnt exist
    action_set_exists = Action_Set.objects.filter(image_set_id_fk = image_set).exists()
    if action_set_exists:
        user_action_set = Action_Set.objects.get(image_set_id_fk = image_set)
    else:
        user_action_set = Action_Set(image_set_id_fk = image_set)
        
        
    # Get Action Set Data, User Image Sizes   
    user_action_set.thumb_w  = action_set_data["thumb_w"]
    user_action_set.thumb_h  = action_set_data["thumb_h"]
    user_action_set.medium_w = action_set_data["medium_w"]
    user_action_set.medium_h = action_set_data["medium_h"]
    user_action_set.large_w  = action_set_data["large_w"]
    user_action_set.large_h  = action_set_data["large_h"]
    
    # Get Action Set Data, Image Quality
    user_action_set.img_qual = action_set_data["quality_val"]
    
    # Get Action Set data, Checkbox responses  
    user_action_set.gab_chk         = action_set_data["gab_chk"]
    user_action_set.minds_chk       = action_set_data["minds_chk"]
    user_action_set.telegram_chk    = action_set_data["telegram_chk"]
    user_action_set.x_chk           = action_set_data["x_chk"]
    user_action_set.fb_chk          = action_set_data["fb_chk"]
    user_action_set.square_chk      = action_set_data["square_chk"]
    
    # Updata tag placment
    user_action_set.tag_placement   = action_set_data['tag_placement']
    
    
    # Set a general check flag to indicate that social media is requested
    if action_set_data["gab_chk"] or action_set_data["minds_chk"] or action_set_data["telegram_chk"] or action_set_data["x_chk"] or action_set_data["fb_chk"]:
        user_action_set.soc_med_chk = True
    else:
        user_action_set.soc_med_chk = False
    

    user_action_set.save()
    
    return





def save_pil_image(pil_image, pil_image_name, fieldname, q_val):
    # Tke the PIL Image Object and Save it as a File on the Filesystem 
    # Then retun the binary contents of that file and its extended name
    
    # pil_image_name eg myimage.jpg
    # Create path for PIL social media image
    xtended_image_name = fieldname + pil_image_name # eg 'thumbnail_myimage.jpg'
    pathname = '/pil_images/' + xtended_image_name # eg '/pil_images/thumbnail_myimages.jpg'
    pil_image_path = settings.MEDIA_ROOT+pathname # Absolute path to the file
    
    # Create empty PIL Image in the Server Filesystem
    default_storage.save(pil_image_path, ContentFile(''))
    
    # pil_mage is the pil image file that has undegone some transformation. Reduce file size and Save
    pil_image.save(pil_image_path, quality = q_val)

    # Open PIL Image as a binary file and extract its data then close
    with open(pil_image_path, 'rb') as f:
        data = f.read()
    f.close()
    
    return((xtended_image_name, data))



def render_processed_images_gallery(image_set):
    user_images = Upload_File.objects.filter(image_set_id_fk = image_set)
    user_action_set = Action_Set.objects.get(image_set_id_fk = image_set)
    
    # First Create an Array containing the URL's for each of the categories of images.
    # Thumbnails, Medium, Large, Social_Media, and their sqaurified counterparts
    thumb_urls = []
    medium_urls = []
    large_urls = []
    social_media_urls = []
    sq_thumb_urls = []
    sq_medium_urls = []
    sq_large_urls = []
    sq_social_media_urls = []
    
    for current_image in user_images:
        # for each image get Processed_Images set
        processed_images_set = Processed_Images.objects.get(upload_file_fk = current_image)
        
        # An array is created to contain the html for the contents of each gallery requested.
        # This can then be rendered as a single page of html with all the images grouped together
        # Or a zip archive to download
        thumb_urls.append(processed_images_set.thumbnail.url)
        medium_urls.append(processed_images_set.medium.url)
        large_urls.append(processed_images_set.large.url)
        
        if user_action_set.square_chk:
            sq_thumb_urls.append(processed_images_set.thumbnail.url)
            sq_medium_urls.append(processed_images_set.medium.url)
            sq_large_urls.append(processed_images_set.large.url)

            
        if user_action_set.soc_med_chk:
            social_media_urls.append(processed_images_set.social_media.url)
            if user_action_set.square_chk:
                sq_social_media_urls.append(processed_images_set.social_media_square.url)
                
     
    
    return "<div>hello</div>"


def render_zip_download_link(request, zip_instance):
    context = {
            "zip_download_path": zip_instance.zipfile.url
    }
    # Rendering the content returns binary data not string
    download_link_binary = render(request, 'hungry_hippo_app/zip_download_link.html', context).content
    
     # decode the returned content from binary back into html string data
    html_link = download_link_binary.decode()
    return html_link



def get_zip_archive(request, image_set, username):
    user_images = Upload_File.objects.filter(image_set_id_fk = image_set)
    user_action_set = Action_Set.objects.get(image_set_id_fk = image_set)
    
    # First Create an Array containing the paths's for each of the categories of images.
    # Thumbnails, Medium, Large, Social_Media, and their sqaurified counterparts
    thumb_paths = []
    medium_paths = []
    large_paths = []
    social_media_paths = []
    sq_thumb_paths = []
    sq_medium_paths = []
    sq_large_paths = []
    sq_social_media_paths = []
    
    # Now get all the images for the image set from Processed Images
    for current_image in user_images:
        # Each image in user_images has a set of processed images, so for each image get Processed_Images set
        processed_images_set = Processed_Images.objects.get(upload_file_fk = current_image)
        
        # An array is created to contain the html for the contents of each gallery requested.
        # This can then be rendered as a single page of html with all the images grouped together
        # Or a zip archive to download
        thumb_paths.append(processed_images_set.thumbnail.path)
        medium_paths.append(processed_images_set.medium.path)
        large_paths.append(processed_images_set.large.path)
        
        if user_action_set.square_chk:
            sq_thumb_paths.append(processed_images_set.thumbnail_square.path)
            sq_medium_paths.append(processed_images_set.medium_square.path)
            sq_large_paths.append(processed_images_set.large_square.path)

        if user_action_set.soc_med_chk:
            social_media_paths.append(processed_images_set.social_media.path)
            if user_action_set.square_chk:
                sq_social_media_paths.append(processed_images_set.social_media_square.path)
    # End for loop
    
    # Now we have an array containing paths to all the files we need to create an archive
          
    #create a path to the users zipfile
    zip_short_name = 'imageset_' + str(image_set.image_set_id) + '.zip' # eg 'imageset_19.zip'
    image_set_zip_path = '/zips/' + username + '/' + zip_short_name     # eg '/zips/artVoo/imageset_19.zip'
    zip_absolute_path = settings.MEDIA_ROOT + f'/zips/{username}/imageset_{image_set.image_set_id}.zip'  # eg /home/full/path/on/filesystem/zips/artVoo/imageset_19.zip'
    
    # Create a file to hold the users zipfile in the filesystem.
    # default_storage will create the directory structure if it doesnt exist yet
    
    # if imageset zipfile exists delete it. There Can Be Only One!
    zipfile_exists = Zipfile_Download.objects.filter(image_set_id_fk = image_set).exists()
    if zipfile_exists:
        Zipfile_Download.objects.get(image_set_id_fk = image_set).delete() 
           
    # Create New Empty Zipfile
    default_storage.save(zip_absolute_path, ContentFile(''))
    
    # Create a ZipFile Object
    #
    # relative_path defines the name of the archive.
    # This will be composed of the label 'imageset_files' and the id of the image set.
    # The path corrosponding to the names of the directories is then added by splitting the pathname of the image
    # so an image with a pathnmae like '...very/long/path/name/processed_images/medium/myimage.jpg'
    # becomes somthing like;
    # {archive_folder}/ => 'imageset_files23/'
    # {img.split('/')[-2]}/{img.split('/')[-1]} => medium/myimage.jpg
    
    with ZipFile(zip_absolute_path, 'w') as zip_object:
        archive_folder = f"imageset_files{image_set.image_set_id}"
        
        # create thumbnail folder in zip and add thumbnail images
        for img in thumb_paths:
            relative_path = f"{archive_folder}/{img.split('/')[-2]}/{img.split('/')[-1]}"
            zip_object.write(img, arcname=relative_path)
            
        # creata medium folder in zip and medium images
        for img in medium_paths:
            relative_path = f"{archive_folder}/{img.split('/')[-2]}/{img.split('/')[-1]}"
            zip_object.write(img, arcname=relative_path)
        
        # create large folder in zip and dd large images   
        for img in large_paths:
            relative_path = f"{archive_folder}/{img.split('/')[-2]}/{img.split('/')[-1]}"
            zip_object.write(img, arcname=relative_path)
            
        # social media zips #################################################  
        if user_action_set.soc_med_chk:
            # create social_media folder in zip and add social_media images
            for img in social_media_paths:
                relative_path = f"{archive_folder}/{img.split('/')[-2]}/{img.split('/')[-1]}"
                zip_object.write(img, arcname=relative_path)
            if user_action_set.square_chk:
                for img in sq_social_media_paths:
                    relative_path = f"{archive_folder}/{img.split('/')[-2]}/{img.split('/')[-1]}"
                    zip_object.write(img, arcname=relative_path)
            
        # squares ###############################################################
        if user_action_set.square_chk:
            # create thumbnail folder in zip and add thumbnail images
            for img in sq_thumb_paths:
                relative_path = f"{archive_folder}/{img.split('/')[-2]}/{img.split('/')[-1]}"
                zip_object.write(img, arcname=relative_path)
                
            # creata medium folder in zip abd add medium images
            for img in sq_medium_paths:
                relative_path = f"{archive_folder}/{img.split('/')[-2]}/{img.split('/')[-1]}"
                zip_object.write(img, arcname=relative_path)
            
            # create large folder in zip and add large images      
            for img in sq_large_paths:
                relative_path = f"{archive_folder}/{img.split('/')[-2]}/{img.split('/')[-1]}"
                zip_object.write(img, arcname=relative_path)
                
        # End with. Zipfile created



    # Check to see if the zip file is created
    if os.path.exists(zip_absolute_path):
        print(f"ZIP file {zip_absolute_path} created")
    else:
        print("ZIP file not created")
        
    # Add Zipfile to the Zipfile_Download Database Model
    # Open file as a binary
    with open(zip_absolute_path, 'rb') as f:
        data = f.read()
    # Copy zip archive into the database
    new_zip = Zipfile_Download(image_set_id_fk = image_set)
    new_zip.zipfile.save(zip_short_name, ContentFile(data))
        
    # Remove the old zipfile from the server and close files
    os.remove(zip_absolute_path)
    zip_object.close()
    f.close() 
    
    return (zip_short_name,render_zip_download_link(request, new_zip))
    
    
    
    
    
    
    
    
def tag_the_image(pil_image_crop,tag_instance, location):
    
    tag_path = tag_instance.tag.path
    
    # Open the tag file in the database and copy it to a pil image. 
    # Copy so that its not working with the original image 
    with Image.open(tag_path) as temp:
        pil_tag = temp.copy()
    
    pil_image_crop_width = pil_image_crop.width
    pil_image_crop_height = pil_image_crop.height
    image_w2h_ratio = pil_image_crop_width / pil_image_crop_height
    
    tag_w2h_ratio = pil_tag.width / pil_tag.height
    print(f"start tag w = {pil_tag.width}")
    print(f"start tag h = {pil_tag.height}")
    print(f"start tag_w2h = {tag_w2h_ratio}")
    
    portrait_image = image_w2h_ratio < 1
    landscape_image = image_w2h_ratio > 1
    square_image = image_w2h_ratio = 1
    


    # Scale tag to be a fifth the size of the image 
    if portrait_image:
        # scale tag for portrait image
    
        # ratio = w/h
        # w = h * ratio
        # h = w / ratio
    
        # height of the tag will be 1/5 of the overall image height
        tag_h = round(pil_image_crop_height /5)

        # width will be scaled to the tag w2h ratio
        tag_w = round(tag_h * tag_w2h_ratio)
    else:
        #scale tag for landscape image

        # width of the tag will be 1/5 of the overall image width
        tag_w = round(pil_image_crop_width /5)

        # width will be scaled to the tag w2h ratio
        tag_h = round(tag_w / tag_w2h_ratio)
        
    print(f"out tag_h = {tag_h}")
    print(f"out tag_w = {tag_w}")
    print(f"out tag_w2h = {tag_w/tag_h}")

    
    transform_image = pil_tag.resize((tag_w, tag_h))
    pil_tag = transform_image.copy()   
    transform_image.close()
    # pil_tag.show()
    
    # Define margins
    margin = 25
    
    # Convert pil_image_crop to RGBA so that transparency is preserved
    if not 'A' in pil_image_crop.getbands():
        converted_image = pil_image_crop.convert("RGBA")
        pil_image_crop = converted_image.copy()
        converted_image.close()
        
    # Convert tag_image to RGBA so that transparency is preserved
    if not 'A' in pil_tag.getbands():
        converted_image = tag_image.convert("RGBA")
        tag_image = converted_image.copy()
        converted_image.close()

    # Tag Positioning
    v_center = round((pil_image_crop_height / 2) - (tag_h / 2))
    h_center = round((pil_image_crop_width /2 )- (tag_w /2))

    upper = margin
    left  = margin
    
    right = pil_image_crop_width - (tag_w + margin )
    lower = pil_image_crop_height - (tag_h + margin)
    
    # Create a blank pil image that the same size as the image it wil be pasted into
    positioned_tag = Image.new("RGBA", (pil_image_crop_width, pil_image_crop_height))

    
    print(f"location = {location}")
    # Overlay tag on image at location specified
    match location:
        case "center":
            positioned_tag.paste(pil_tag, (h_center, v_center))
            #test  = Image.composite(pil_image_crop, positioned_tag, positioned_tag)
            #test2 = Image.composite(pil_image_crop, positioned_tag, pil_image_crop)
            #test3 = Image.blend(pil_image_crop, positioned_tag, 0.5)
            #pil_image_crop.paste(positioned_tag)
            
            pil_image_crop = Image.alpha_composite(pil_image_crop, positioned_tag)
        case "top_left":
            positioned_tag.paste(pil_tag, (left, upper))
            pil_image_crop = Image.alpha_composite(pil_image_crop, positioned_tag)
        case "top_right":
            positioned_tag.paste(pil_tag, (right, upper))
            pil_image_crop = Image.alpha_composite(pil_image_crop, positioned_tag)
        case "lower_left":
            positioned_tag.paste(pil_tag, (left, lower))
            pil_image_crop = Image.alpha_composite(pil_image_crop, positioned_tag)
        case "lower_right":
            positioned_tag.paste(pil_tag, (right, lower))
            pil_image_crop = Image.alpha_composite(pil_image_crop, positioned_tag)
        case "no_tag":
            pass
        case _:
            positioned_tag.paste(pil_tag, (margin, margin))
            pil_image_crop = Image.alpha_composite(pil_image_crop, positioned_tag)
        
    # Convert to RBG
    converted_image = pil_image_crop.convert("RGB")
    pil_image_crop = converted_image.copy()
    converted_image.close()

    return pil_image_crop






def scale_width(baseimage_w2h_ratio, process_image_h):
    #  base_w and base_h represent the width and height of a base image.
    #  From this the image width : height ratio is calculated
    #
    #  Given an process_image height the functio will 
    #  return the width corrosponsing to this height
    
    process_image_width = process_image_h * baseimage_w2h_ratio
    return round(process_image_width)
      
def scale_height(baseimage_w2h_ratio, process_image_w):
    #  base_w and base_h represent the width and height of a base image.
    #  From this the image width : height ratio is calculated
    #
    #  Given an process_image width the function will 
    #  return the height corrosponsing to this width
    
    process_image_height = process_image_w / baseimage_w2h_ratio
    return round(process_image_height)
      
    
     

def create_master_image(image_instance, user_action_set, processed_image_set):
    # Carry out the actions in the action set and save the master image to the database Processed_Images table
    # Define absolute path to save PIL Image 
    # image_inastance is the current uploaded file in the database being processed
    
    # Get Image_set for this image_instance
    image_set = image_instance.image_set_id_fk
    
    # Open original image_inastance and make a copy so we arnt working with the original
    with Image.open(image_instance.image_file.path) as original_image:
        pil_image = original_image.copy()
            
    #  Get image filename and path to save master pil image later
    pil_image_name = get_shortname(image_instance.image_file.name)
    pathname = '/pil_images/' + pil_image_name
    pil_image_path = settings.MEDIA_ROOT + pathname # Absolute path to the file
    # Create empty PIL Master Image in the Server Filesystem. 
    # default_storage will create the directory structure if it doesnt exist yet
    default_storage.save(pil_image_path, ContentFile(''))
    
    print(f"Processing Image {pil_image_name}")
    
    
    ###########################################################################################################
    #
    # If the image being processed has different dimensions and height/width ratio to the baseimage, 
    # it will cause the crop not to match up with the image. Off canvas or in odd locations
    # The greater the difference the greater the error. 
    # 
    # This can be solved by either
    # 
    # 1. Normalise the image to fit within the baseimage dimensions/aspect ratio before processing it further.
    # 2. Scale the crop to match the image
    #
    # For the purposes if this app, The best option is probably to scale the crop dimensions to the image being processed
    # This will then adjust the crop to the image and maintain the aspect ratio of the original image being adjusted
    
    # Get Baseimage the user was working with
    baseimage = Upload_File.objects.filter(image_set_id_fk = image_set).get(baseimage = True) 
    with Image.open(baseimage.image_file.path) as original_image:
        pil_baseimage = original_image.copy()
    
    # Get base image dimensions
    baseimage_h = pil_baseimage.height
    baseimage_w = pil_baseimage.width
    baseimage_w2h_ratio = baseimage_w / baseimage_h 
    
    # Get PIL Cropper Instance
    pil_cropper_set = PIL_Cropper.objects.get(image_set_id_fk = image_set)
    
    

    
    
    
    # Get baseimage crop dimensions 
    baseimage_left  = pil_cropper_set.pil_crop_left
    baseimage_upper = pil_cropper_set.pil_crop_upper
    baseimage_right = pil_cropper_set.pil_crop_right
    baseimage_lower = pil_cropper_set.pil_crop_lower
    baseimage_crop_width  = pil_cropper_set.pil_crop_width
    baseimage_crop_height = pil_cropper_set.pil_crop_height
    baseimage_crop_w2h_ratio = baseimage_crop_width / baseimage_crop_height
    print(f"baseimage crop width  = {baseimage_crop_width}")
    print(f"baseimage crop height = {baseimage_crop_height}")
    print(f"baseimage crop w2h ratio = {baseimage_crop_w2h_ratio}")
    
    # Determine the percentage values of the positions of the crop
    left_x_percent  = baseimage_left/baseimage_w  # The left position as a decimal percentage of the width of the baseimage
    right_x_percent = baseimage_right/baseimage_w # The right position 
    upper_y_percent = baseimage_upper/baseimage_h # The upper position 
    lower_y_percent = baseimage_lower/baseimage_h # The lower position 
    
    # Now Apply those percentages to the image being processed to get the new crop values
    left  = pil_image.width  * left_x_percent
    upper = pil_image.height * upper_y_percent
    right = pil_image.width  * right_x_percent
    lower = pil_image.height * lower_y_percent 
    
    ###########################################################################################################
    

      # Rotate PIL Image
    image_rotation = pil_cropper_set.pil_rotation
    transformed_image = pil_image.rotate(image_rotation,expand=True)
    pil_image = transformed_image
    # pil_image.show()          

    
    # Crop PIL Image. crop function takes a tuple of the following format crop((left, upper, right, lower))
    transformed_image = pil_image.crop((left, upper, right, lower))
    pil_image_crop = transformed_image.copy()
    transformed_image.close()
    
    # Tag Image
    image_set = user_action_set.image_set_id_fk
    # image_set = Image_Set.objects.get(image_set_id = user_image_set_id)
    tag_exists = Imagetag.objects.filter(image_set_id_fk = image_set).exists()
    if tag_exists:
        tag = Imagetag.objects.get(image_set_id_fk = image_set)
        tagged_image =  tag_the_image(pil_image_crop, tag, user_action_set.tag_placement)
        pil_image_crop = tagged_image
        
    # pil_image_crop.show()
        
    ######################################################################################
    #
    #   At this point
    #
    #   1. The crop has been scaled and adapted to the pil_image
    #   2. The crop has been applied and the image is now cropped.
    #
    # Before the image can be resized as per the crop dimensions in the action set,
    # it must first be in a container with the same aspect ratio of the basimage crop, 
    # otherwise it will end up being squeezed/ stretched. 
    # (Assumption is that the folder uploaded will contain images with various different dimensions)
    #
    # 1.    Create a container with the same aspect ratio of the baseimage crop
    #       The containers dimensions are determined by the longest side of the pil image being processed
    # 2.    Paste the pil_image in the center of the container

    # if the image being processed height > width
    #   This basetemplate height is the same width as the image being processed
    # else
    #   This base width is the same as the image being processed
    #  create the baseimage
    #  paste the pil_image into the center of the baseimage
            
            
    #################################################
    #
    # Normalise the Image
    
    # In normalising the image there are four things that are relevant
    # 1. The baseimage width and height
    # 2. The baseimage crop width and height
    # 3. The pil_image width and height ( The image being processed)
    # 4. The pil_image crop width and height
    
    # Determine pil_image_crop format
    portrait  = pil_image_crop.height > pil_image_crop.width
    landscape = pil_image_crop.height < pil_image_crop.width
    square    = pil_image_crop.height == pil_image_crop.width
    pil_image_crop_w2h_ratio = pil_image_crop.width / pil_image_crop.height
    

    # Define path for the normalization template 
    template_name = 'temp.jpg'
    pathname = f"/pil_image/{template_name}"
    template_path = settings.MEDIA_ROOT+pathname # Absolute path to the file

    # Create a Template image with the same w/h ratio as the baseimage_crop to contain the pil_image_crop
    if pil_image_crop_w2h_ratio < baseimage_crop_w2h_ratio: # scale the height to the width
        pil_container_height = pil_image_crop.height
        pil_container_width = scale_width(baseimage_crop_w2h_ratio, pil_container_height)
        # Portrait format so margin left and right       
        # calculate where the pasted image should be to center it
        margin = round((pil_container_width - pil_image_crop.width)/2)
        x_offset = margin
        y_offset = 0
        print(f"calculation width")
    else:
        # pil_image_crop_w2h_ratio is wider than the basecrop_w2h_ratio
        # This means set the width to the pil_image_crop width and scale the height in line with the baseimage_crop_wsh_ratio
        pil_container_width = pil_image_crop.width
        pil_container_height = scale_height(baseimage_crop_w2h_ratio, pil_container_width)
        
        # landscape format so margin top and bottom
        # calculate where the pasted image should be to center it
        margin = round((pil_container_height - pil_image_crop.height)/2)
        x_offset = 0
        y_offset = margin
        print(f"calculating height")

    print(f"pil container width  = {pil_container_width}")
    print(f"pil container height = {pil_container_height}")
    print(f"pil container w2h ratio = {pil_container_width / pil_container_height}")
    # Create temporay image for the template
    pil_container = Image.new("RGB", (pil_container_width, pil_container_height), ImageColor.getrgb('white'))
    
    print(f"pil_image_crop width  = {pil_image_crop.width}")
    print(f"pil_image_crop height = {pil_image_crop.height}")
    print(f"pil_image_crop_w2h ratio = {pil_image_crop.width / pil_image_crop.height}")
    
    # place image_file in the middle of the new canvas
    pil_container.paste(pil_image_crop, (x_offset, y_offset))
    
    pil_image_crop = pil_container.copy()
    pil_container.close()

    #
    #   End Normalising the image
    ################################################     
        

    # Save PIL master Image, Highest Quality, Original Natural size and close
    pil_image_crop.save(pil_image_path, quality=100)
    pil_image_crop.close()
    
    # Open PIL Image as a binary file
    with open(pil_image_path, 'rb') as f:
        data = f.read()
    
    # Save to Processed Image Set, master ImageField using ContentFile
    if (processed_image_set.master):
        processed_image_set.master.delete(save=True)
        
    # Create Master Image that all the resizes are based upon
    processed_image_set.master.save(pil_image_name, ContentFile(data))
    # Close the PIL Binary content file
    f.close()
    
    
    # Create Master Image that all the resizes are based upon
    
    master_path = processed_image_set.master.path
    print(f"master path = {master_path}")
    try:
        with Image.open(master_path) as master_img:
            master_img.show()
    except Exception as e:
        print(f"Cant open {master_path}. ERROR: {e}")
    
    # pil_master_image = Image.open(pil_image_path)
    # pil_master_width = pil_master_image.width
    # pil_master_height = pil_master_image.height
    
    # pil_master_image.show()
    # master image created and saved to ImageField in Processed_Images. The pil_image can now be safely Deleted 
    # os.remove(pil_image_path) 
    
    return 
















def create_resized_image(pil_master_image, dataset):
    # General function that takes a pil image then resizes it and adds it to the database
    '''
    # example
    dataset = {
        "namespace"         : "_thumb_",
        "width"             : user_action_set.thumb_w,
        "height"            : user_action_set.thumb_h,
        "pil_image_name"    : pil_image_name,
        "quality"           : quality,
        "fieldname"         : processed_image_set.thumbnail,
        "square_chk"        : square_chk,
        "sqaure_fieldname"  : square_fieldname  
    }
    '''
    #  need to supply the field that is being updated

    # Make a copy of the master image to resize
    pil_image = pil_master_image.copy()
    width = dataset["width"]
    height = dataset["height"]
    
    transformed_image = pil_image.resize((width, height))
    pil_image = transformed_image        

    # get PIL Image_name and binary data
    namespace = dataset["namespace"]
    (pil_image_name, pil_image_data) = save_pil_image(pil_image, dataset["pil_image_name"], namespace, dataset["quality"]) 

    # Assign to ImageField
    dataset["fieldname"].save(pil_image_name, ContentFile(pil_image_data))
    
    # Squarify
    if dataset["square_chk"]:
        namespace = "sq_"+namespace   
        pil_sq_thumb_image = squarify_image(pil_image)
        
        # get PIL Image_name and binary data
        (pil_sq_thumb_image_name, pil_sq_thumb_image_data) = save_pil_image(pil_sq_thumb_image, dataset["pil_image_name"], namespace, dataset["quality"]) 
        # Assign to ImageField
        dataset["square_fieldname"].save(pil_sq_thumb_image_name, ContentFile(pil_sq_thumb_image_data))
        
        pil_sq_thumb_image_path = settings.MEDIA_ROOT + '/pil_images/' + pil_sq_thumb_image_name
        os.remove(pil_sq_thumb_image_path)
        pil_sq_thumb_image.close() 
        
    pil_image_path = settings.MEDIA_ROOT + '/pil_images/' + pil_image_name
    os.remove(pil_image_path)
    pil_image.close() # I think removing the image might automatically close it but this doesnt hurt either  AFAIK
    
    



@csrf_exempt
@login_required
def process_batch(request):
    print("### API: Process Batch")
    
    ########################################################################################
    #
    # Validate Request
    #
    if request.method != 'PUT':
        return JsonResponse({'error': 'API: Malforned request. PUT method required'}, status = 301)
    
    # Get Current User and User Profile
    current_user = request.user
    
    # Verify User_Profile exists for current user
    user_profile_exists = User_Profile.objects.filter(user_id_fk = current_user).exists()
    if user_profile_exists:
        user_profile = User_Profile.objects.get(user_id_fk = current_user)
    else:
        return JsonResponse({"API: User Profile cant be found"}, status=404)
    
    # Unpack data from request
    data = json.loads(request.body)
    
    # Verify User has Uploaded Images to Process and Get Image Set 
    user_image_set = data.get("image_set_id")
    if user_image_set == 'no images uploaded':
        return JsonResponse({'message': 'API: No images uploaded'}, status = 401)
    
    #############################################################################     
    #
    #   Retrieve Data
    #
    
    # Get Image Set
    image_set = Image_Set.objects.get(image_set_id = user_image_set)
    print(f"API: Image Set = {image_set.pk}")
    
    # Retrieve Cropper data
    cropper_data = data.get("cropper_data")

    # Updata database with action set data and PIL calculations data
    action_set_data = data.get("action_set_data")
    process_action_set_data(action_set_data, image_set)
    process_cropper_data(cropper_data, image_set)
    
    # Retrieve the Action_Set Instance for this Image_Set
    user_action_set = Action_Set.objects.get(image_set_id_fk = image_set)
    quality = user_action_set.img_qual
    print(f"quality = {quality}")
    
    # Retrieve the Images to be Processed
    uploaded_images = Upload_File.objects.filter(image_set_id_fk = image_set)
    
    
    ####################################################################################
    # 
    #   this is really stoopid
    
    # # Update Baseimage Image if it has been changed
    baseimage_id = data.get("baseimage_id")
    first_image = Upload_File.objects.first() # The default baseimage

    # Find the current baseimage and set the baseimage status to False
    current_baseimage = Upload_File.objects.filter(image_set_id_fk = image_set).get(baseimage = True)
    current_baseimage.baseimage = False
    current_baseimage.save()
    
    # Find the upload file where the pk = the basimage_id. Set its basimage status to true
    new_baseimage = Upload_File.objects.get(pk = baseimage_id)
    new_baseimage.baseimage = True
    new_baseimage.save()
    
    #
    #
    ######################################################################################



    ##################################################################################
    #
    # Iterate through each image and carry out transformations
    #
    for image_instance in uploaded_images:
                
        # Create an Instance of Processed_Images to store them
        # Each uploaded image will have 3 - 8 related processed images stored in this instance
        
        # If the processed_images set exist, delete it and create a new one (This is for when the user re-runs the batch proceess)
        Processed_Images.objects.filter(upload_file_fk = image_instance).delete() # if it doesnt exist filter returns none and nothing happens. Otherwise its deleted    
           
        # Create a fresh set of processed images 
        processed_image_set = Processed_Images(upload_file_fk = image_instance)
        processed_image_set.save()
        
        # Get General Image Information
        current_image = image_instance.image_file
        
        # Get image name from the path to give the PIL Image the same name 
        pil_image_name = get_shortname(current_image.name)
        
        # Create Master Image
        create_master_image(image_instance, user_action_set, processed_image_set)
        
        # Open the master image in PIL
        pil_master_image = Image.open(processed_image_set.master.path)
        


        
        
        ################################################################################################################
        #
        # Apply resizes to the master image to produce, thumbnail, medium, large social media square format images
        #
        ################################################################################################################

        # Create social media optimized image if requested. This is optimally 1200 x 640 -> 1200 x 1200. 

        if user_action_set.soc_med_chk:
            pil_sm_image = pil_master_image.copy()
            portrait = pil_sm_image.height > pil_sm_image.width
            if portrait:
                # scale height to 1200
                # scale width accordingy
                scale = 1200 / pil_sm_image.height
            else:
                #lanscape
                scale = 1200 / pil_sm_image.width
            
            new_height = int(pil_sm_image.height * scale)
            new_width = int(pil_sm_image.width * scale)
            
            ########################################################################################################
            
            dataset = {
                "namespace"         : "soc_med_",
                "width"             : new_width,
                "height"            : new_height,
                "pil_image_name"    : pil_image_name,
                "quality"           : quality,
                "fieldname"         : processed_image_set.social_media,
                "square_chk"        : user_action_set.square_chk,
                "square_fieldname"  : processed_image_set.social_media_square  
            }
            create_resized_image(pil_master_image, dataset)
        # End If
            
        ########################################################################################################
        # Create Thumbnail Images
        dataset = {
            "namespace"         : "thumb_",
            "width"             : user_action_set.thumb_w,
            "height"            : user_action_set.thumb_h,
            "pil_image_name"    : pil_image_name,
            "quality"           : quality,
            "fieldname"         : processed_image_set.thumbnail,
            "square_chk"        : user_action_set.square_chk,
            "square_fieldname"  : processed_image_set.thumbnail_square  
        }
        create_resized_image(pil_master_image, dataset)
        
        #######################################################################################################
        # Create Medium Sized Images
        dataset = {
            "namespace"         : "medium_",
            "width"             : user_action_set.medium_w,
            "height"            : user_action_set.medium_h,
            "pil_image_name"    : pil_image_name,
            "quality"           : quality,
            "fieldname"         : processed_image_set.medium,
            "square_chk"        : user_action_set.square_chk,
            "square_fieldname"  : processed_image_set.medium_square  
        }
        create_resized_image(pil_master_image, dataset)
        
        # #########################################################################################################
        # Create Large Sized Images
        dataset = {
            "namespace"         : "_large_",
            "width"             : user_action_set.large_w,
            "height"            : user_action_set.large_h,
            "pil_image_name"    : pil_image_name,
            "quality"           : quality,
            "fieldname"         : processed_image_set.large,
            "square_chk"        : user_action_set.square_chk,
            "square_fieldname"  : processed_image_set.large_square  
        }
        create_resized_image(pil_master_image, dataset)
        
        # #########################################################################################################       

        # Close PIL Master Image
        pil_master_image.close()   

    # End for loop iteration Processing Images
    

    
    # Get path to zipFile image_set_zip_path = '/zips/' + username + '/' + zip_short_name
    zipname, zipfile_html_link = get_zip_archive(request, image_set, current_user.username)
    
    print(f"zip_path: zip_archive_path")
    

            
    return JsonResponse({'message': 'Success',
                         'zipname': zipname,
                         'zipfile_html_link': zipfile_html_link}, status=201)




























