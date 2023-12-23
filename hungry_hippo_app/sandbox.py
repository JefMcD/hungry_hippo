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

# Forms
from django.views.decorators.csrf import csrf_exempt
from .forms import *

# Image Handling
from PIL import Image, ImageColor
from django.core.files import File
from django.core.files.images import ImageFile

from .api import *



##############################################################
#   Notes on ZipFile
'''
    Saving ZipFile and Defining the archive directory structure
    
    # Create a ZipFile Object
    with ZipFile(zip_absolute_path, 'w') as zip_object:
        # Create a folder in the zip archive to store the files
        archive_folder = 'imageset_files'
    
    # Add files to the zip archive with a specific name (arcname) to avoid preserving the directory structure
    for img in thumb_paths:
        # Determine the relative path of the file within the archive
        relative_path = f"{archive_folder}/{img.split('/')[-1]}"  # Change this logic as needed
        
        # Add the file to the archive with the specified relative path (arcname)
        zip_object.write(img, arcname=relative_path)

    
    relative_path = f"{archive_folder}/{img.split('/')[-1]}"


    img.split('/'): 
    This part of the line uses the split('/') method on the img variable, which is assumed to be a string 
    representing the absolute path to an image file. The method splits the string into a list using the 
    forward slash ("/") as the delimiter. This effectively creates a list of directory names and the filename.

    img.split('/')[-1]: 
    The [-1] index is used to retrieve the last element of the list obtained from the split. 
    In the context of a file path, this corresponds to the filename itself.

    f"{archive_folder}/{img.split('/')[-1]}": 
    This is an f-string, a feature in Python that allows you to embed expressions inside string literals. 
    In this case, it creates a new string that combines the archive_folder variable 
    (the folder name you want within the zip archive) with the filename obtained from the original img path.

    So, overall, the line is constructing a relative_path variable that represents the desired location 
    of the file within the zip archive. It places the file inside the specified archive_folder while 
    keeping the original filename. This ensures that all the files in the zip archive will be located 
    in the same subfolder (imageset_files in this case) rather than preserving their original directory structure.





    # Create a ZipFile from a Folder and subfolders contents
    with ZipFile(zip_absolute_path, 'w') as zip_object:
        # Traverse all files in directory
        for folder_name, sub_folders, file_names in os.walk(processed_folder):
            for filename in file_names:
                # Create filepath of files in directory
                file_path = os.path.join(folder_name, filename)
                # Add files to zip file
                zip_object.write(file_path, os.path.basename(file_path))

'''    
    
    
    
def analyse_imageFile_Vs_PILFile(request, user_image_set):
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

    
    # Create Upload_tag instance associated with the Image_Set
    image_tag = request.FILES.get('tag_upload')
    print(f"image_tag => {image_tag}")
    new_tag_image = Imagetag(image_set_id_fk = image_set,
                            tag = image_tag)
    new_tag_image.save()
    
    # get form data from the request
    print(f"request.POST => {request.POST}")
    print(f"request.FILES => {request.FILES}")
    print(f"request.FILES => {request.FILES['tag_upload']}")
    
    # Return the Url of the file on the server to the Javascript Client
    
    # iterate throgh the images in the FILES
    # Create an Instance of Image_Files for each image in the Image_Set

    pil_image_name = get_imagename(new_tag_image.tag.name)
    django_tag_name = new_tag_image.tag.name
    django_tag_path = "Full (V.long) abs path to the file...jpg"
    django_tag_url = new_tag_image.tag.url
    
    # Create a PIL File from the tag image
    # This takes the absolute path to the file and then returns a PIL Image object
    
    #create a new Imagetag instance to save the processed pil tag to
    new_pil_image = Imagetag(image_set_id_fk = image_set)
    from django.core.files.uploadedfile import InMemoryUploadedFile
    
    # Open the tag from the database as a PIL image
    pil_Image_tag = Image.open(new_tag_image.tag.path)
    rotate_pil_tag = pil_Image_tag.rotate(90, expand=True)
    
    # pil_name = rotate_pil_tag.filename // This is an error because only images created by PIL have a filename attribute.
    pil_format = rotate_pil_tag.format # format is 'none' for images not created by PIL. ie this image was opened not created
    pil_width = rotate_pil_tag.width
    pil_height = rotate_pil_tag.height
    # pil_info = rotate_pil_tag.info    # A dictionary containing associated image data # Created error
    pil_size = rotate_pil_tag.size      # A tuple width, size
    pil_tell = rotate_pil_tag.tell()    # Returns the current frame number. Dont know why this is needed for am ImageFile
    
    # IMage Bands: eg Red, Green, Blue and Alpha. Each Pixel has one value for each band
    # Other Bands, RGB, CMYK, LAB, HSV
    # PNG Images have an A(lpha) channel, JPG's do not 
    pil_bands = rotate_pil_tag.getbands()
    print(f"pil_bands = {pil_bands}")
    
    
    ###################################################################################################
    
    pil_image_name = get_imagename_and_extension(new_tag_image.tag.name)
    
    # Can I save the PIL Image to MEDIA_ROOT 
    # and then define the ImageFile field to point to this location manually
    # https://stackoverflow.com/questions/1308386/programmatically-saving-image-to-django-imagefield
    
    pill_path = settings.MEDIA_ROOT+pil_image_name
    rotate_pil_tag.save(pill_path,quality=70)

    # Create a New Instance in the Databse to store the PIL Image
    django_pil_image = Imagetag(image_set_id_fk = image_set)
    
    # This following doesnt work. 
    # You cant directly assign a PIL Image to a Django ImageField, 
    # (the way you might assign the image contained in request['FILES']) 
    #       django_pil_image.tag = rotate_pil_tag
    #       django_pil_image.save() //=> error
    
    #  YOu have to close the image and then open it as a Binary File 
    #  then you can save it to the ImageFIle in the database
    #
    #       rotate_pil_tag.close()
    #       with open(pill_path, 'rb') as f:
    #           data = f.read()
    #    
    #       django_pil_image.tag.save('test_pil.png', ContentFile(data))
    
    ##########################################################################################
    
    # Saving the PIL Image to Processed_Images
    image_set = Image_Set.objects.get(pk = 55)
    test_image = Upload_File.objects.filter(image_set_id_fk = image_set).first()
    print(f"Upload File Id = {test_image.pk}")

    # Create new processed images instance    
    processed_test_image = Processed_Images(upload_file_fk = test_image)
    processed_test_image.save() # This is necessary to be able to update image_file with new data for the PIL
    
    # Create PIL Image on the Filsystem
    # get filename and 
    # Save to MEDIA_ROOT/processed_images/ 
    
    ###############################################################################################################
    ###############################################################################################################
    #
    # Django 
    #
    # The model defines upload_to = 'processed_images'. 
    # Django will automatically upload any files assigned to an ImageField to this folder
    # A filename in Django can not contain the character '/' or '..' This will cause a path traversal error
    # The filename must be the filename and nothing more eg 'my_image.jpg'
    # Ultimately the image will be stored in MEDIA_ROOT/'upload_to='/filname.xxx
    #
    # PIL
    #
    # The PIL Image is saved to any folder eg one called 'pil_images'
    # The PIL Image can be saved anywhere and have any filename
    # The PIL image paths can be absolute, containing '/', so presumeably they dont get checked by the Django scurity framework
    #
    # create path to save the PIL Image
    filename = get_imagename_and_extension(test_image.image_file.name)
    pathname = '/pil_images/'+filename
    pil_image_path = settings.MEDIA_ROOT+pathname # Absolute path to the file
    
    # Use DJango Files API to touch the Filesystem path and create an empty File and directory structure if it doesnt exist
    # PIL requires the absolute path to the file. ContentFile('') creates an empty file 
    default_storage.save(pil_image_path, ContentFile(''))
    
    # Open ImageFile in PIL, rotate and save in pil_images folder
    new_pil = Image.open(test_image.image_file.path)
    new_pil_rotated = new_pil.rotate(90)
    new_pil_rotated.save(pil_image_path, quality=70)
    new_pil_rotated.close()

    # The PIL Image on the filesystem is opened as a binary file 
    print(f"pil_path: {pil_image_path}")
    # Save PIL in ImageFile
    with open(pil_image_path, 'rb') as f:
        data = f.read()
        
    # The binary file is then assigned to the ImageField using ContentFile() together with a filename
    # ContentFile() is a Django class that wraps a python file containing data.

    # The Model creates an ImageField for the image and copies the image into 
    # whatever 'upload_to' is defined as. In this case the folder is 'processed_images' 
    
    # The filename cant contain the '/' character or '..' as these trigger an error
    
    processed_test_image.master.save(filename, ContentFile(data))
    
    # Remove PIL Image
    os.remove(pil_image_path)
    
    #######################################################################################################
    #######################################################################################################
    
    print(f"processed_test_image.url = {processed_test_image.master.url}")
    print(f"processed_test_image.name = {processed_test_image.master.name}")
    print(f"processed_test_image.path = {processed_test_image.master.path}")
    
    print(f"pil_format = {pil_format}")
    print(f"PIL Immage: {pil_Image_tag}")

    return JsonResponse({
            "message":"Tag successfully uploaded", 
            "pil_bands"       : pil_bands,
            "pil_image_name"  : pil_image_name,
            "django_tag_name" : django_tag_name,
            "django_tag_path" : django_tag_path,
            "django_tag_url"  : django_tag_url}, status=201)
    
    
    
    
    
    






































@csrf_exempt
@login_required
def process_batch(request):
    print("### API: Process Batch")
    
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
    
    # get data from request
    data = json.loads(request.body)
    
    # Get Image Set
    user_image_set = data.get("image_set_id")
    print(f"user_image_set = {user_image_set}")
    if user_image_set == 'default':
        return JsonResponse({'message': 'API: No images uploaded'}, status = 401)
        

    # Get Image Set
    image_set = Image_Set.objects.get(image_set_id = user_image_set)
    
    #########################################################################
    # Unpack request PUT data
    #########################################################################
    ### Notes on getting the data from the request
    #
    ## First the data is retieved from the Json string sent by the Fetch request (data = json.loads(request.body)) 
    ## This returns a dictionary of key: value pairs.
    ## These are accessed using the python get() method "data.get()"" and their contents accessed using the [] bracket notation
    ##
    ##  data = json.loads(request.body)
    ##                      crop_data = data.get("cropper_data")
    ##  or drilling down
    ##                      alt_data  = data["cropper_data"]["crop_x_offset"]
    ##                      alt_data2 = data.get("cropper_data")["crop_y_offset"]
    
    # Get Cropper crop data
    cropper_data = data.get("cropper_data")
    crop_x_offset = int(cropper_data["crop_x_offset"])
    crop_y_offset = int(cropper_data["crop_y_offset"])
    crop_width = int(cropper_data["crop_width"])
    crop_height = int(cropper_data["crop_height"])
    
    # Get rotation
    image_rotation =int(cropper_data["image_rotation"])
    
    # Retrieve the Action_Set for this Image_Set
    user_action_set = Action_Set.objects.get(image_set_id_fk = image_set)
    
    # Get Action Set Data, User Image Sizes   
    thumbnail_size = user_action_set.thumbnail_size
    preview_size = user_action_set.preview_size
    large_size = user_action_set.large_size
    
    # Get Action Set data, Checkbox responses
    gab_checkbox = user_action_set.gab_chk
    minds_checkbox = user_action_set.minds_chk
    telegram_checkbox = user_action_set.telegram_chk
    x_checkbox = user_action_set.x_chk
    facebook_checkbox = user_action_set.fb_chk
    square_checkbox = user_action_set.square_chk
    print(f"API: square_checkbox => {square_checkbox}")
    
    
    
    # PIL Co-ordinates. image origin is 0,0 left upper corner
    # crop parameter is a tuple. (left, upper, right, lower) or (x1, y1, x2, y2)
    left = crop_x_offset
    upper = crop_y_offset
    right = crop_x_offset + crop_width
    lower = crop_y_offset + crop_height
    # Pillow rotation is 0 -> 360 moving counter-clockwise or or 0 -> -360 moving clockwise 
    # However, the User interface rotation slider is centered on 0 between -180 and 180, 
    # Fortunatley PIL does negative rotations so the the rotation is converted to PIL format by simply multiplying by -1
    image_rotation = image_rotation * -1
    
    # Update Action Set with PIL Crop Data
    
    
    # Get Images to Process
    image_files_query = Upload_File.objects.filter(image_set_id_fk = image_set)
    
    # iterate through each image in this Image Set and process with PIL/Pillow
    for image_instance in image_files_query:
        print(f"Processing image:  Image Set ({image_instance.image_set_id_fk.pk}): {image_instance.image_file.name}")
        
        # Open Image with Pillow
        image_file = image_instance.image_file
        work_image = Image.open(image_file)

        # Rotate Image
        rotation = work_image.rotate(image_rotation,expand=True)
        
        # crop function takes a tuple of the following format
        crop_and_rotate = rotation.crop((left, upper, right, lower))
        #crop_and_rotate.show()
        
        # If Image Tag Exists tag the image
        
        # Create instance of Processed_Images
        print(f"creating processed_images instance")
        new_processed_images = Processed_Images()
        new_processed_images.upload_file_fk = image_instance
        print(f"saving empty processed images instance")
        new_processed_images.save()
        print(f"done")
        print(f"creating fullsize image in PIL")
        
        # Save processed PIL image
        fullsize_image = crop_and_rotate
        
        # create a unique name on the filesystem
        # get image filename
        imagename = get_imagename(image_instance.image_file.name)
        
        # MEDIA_ROOT = '/home/artillery/webdev-apps/courses/CS50/Capstone/hungry_hippo/user_uploads'
        # prcessed_files = 'processed'
        # user = current_user.username
        # image_set = 'set' + int(image_set.pk)
        # action_set = 'actions'
        
        # Gallery created in
        # MEDIA_ROOT/username/gallery
        # Inside there is a folder containing the processed files. standard and square
        # Each has a folder for thumbnails, preview, large, soc_med, fullsize
            
        standard_gallery_path = os.path.join(settings.MEDIA_ROOT, current_user.username, 'standard_gallery') 
        square_gallery_path = os.path.join(settings.MEDIA_ROOT, current_user.username, 'square_gallery') 
        new_processed_images.standard_gallery = standard_gallery_path
        new_processed_images.square_gallery = square_gallery_path
        print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
        print(f"standard gallery: {standard_gallery_path}")
        print(f"square gallery: {square_gallery_path}")
        
            
        name = 'fullsize_' + imagename  + '.jpg'
        print(f"name = {name}")
            
        # Save PIL Image to the Fullsize folder in the standard gallery
        pil_absolute_path = standard_gallery_path
        fullsize_img_path = os.path.join(standard_gallery_path, new_processed_images.fullsize_folder_std , name)
        print(f"PIL path : {pil_absolute_path}")
        
        django_relative_path = os.path.join(current_user.username, 'standard_gallery')
        django_image_path = os.path.join(django_relative_path, new_processed_images.fullsize_folder_std , name)
        print(f"DJANGO path: {django_image_path}")
        
        print(f"fullname = {fullsize_img_path}")

        if(default_storage.exists(fullsize_img_path)):
            print(f"image Already Exists")
        else:
            print(f"Creating Image")
            
            print(f"stat path")
            # Uses DJango Files API to touch the Filesystem path and create an empty File and directory structure if it doesnt exist
            # PIL requiures the absolute path to the file
            touchpath = default_storage.save(fullsize_img_path, ContentFile(''))
            
            # Save PIL Image to the new path (YOu could probably pass this as a parameter to ContentFile() and save this step, but I prefer this way)
            fullsize_image.save(fullsize_img_path)
            print(f"PIL Image saved")
        
            # Save PIL Image into Processed_Images
            # Looks like this requires converting a PIL image into an ImageField
            # https://stackoverflow.com/questions/32945292/how-to-save-pillow-image-object-to-django-imagefield/45907694
            # https://stackoverflow.com/questions/3723220/how-do-you-convert-a-pil-image-to-a-django-file
            # https://docs.djangoproject.com/en/4.1/topics/files/
            print(f"Saving PIL Image to Database")
            
            # ImageFiles will thrwo a path traversal erro if you use an absolute path so you cant use the PIL path
            # The Django path requires to be relative to MEDIA_ROOT
            from django.core.files.uploadedfile import InMemoryUploadedFile
            new_processed_images.fullsize.save(
                django_image_path, InMemoryUploadedFile(
                                        fullsize_image,       # file
                                        None,                 # field_name
                                        django_image_path,    # file name
                                        'image/jpeg',         # content_type
                                        fullsize_image.tell,  # size
                                        None))
            
            #new_processed_images.fullsize = fullsize_image
            #new_processed_images.save()
            print(f"Image added to Processed_Images")

        
        # Iterate through the action_set user_image_sizes and create that resized image
        '''
        for new_size in user_image_sizes:
            print(f"resize_image key : {new_size}, value : {user_image_sizes[new_size]}")
            resize = int(user_image_sizes[new_size])
            
            new_image = resize_image(fullsize_image, resize)

            # Add new image to the Processed Images Table
            match new_size:
                case 'thumbnail':
                    new_processed_images.thumbnail = new_image
                    if(square_checkbox == 'on'):
                        square_image = squarify_image(new_image)
                        new_processed_images.thumbnail_square = square_image
                case 'preview':
                    new_processed_images.preview = new_image
                    if(square_checkbox == 'on'):
                        square_image = squarify_image(new_image)
                        new_processed_images.preview_square = square_image
                case 'large':
                    new_processed_images.large = new_image
                    if(square_checkbox == 'on'):
                        square_image = squarify_image(new_image)
                        new_processed_images.large_square = square_image
                    
        '''

        # new_processed_images.save()
        print(f"image_set_id = {user_image_set}")

            
        
    # Render an Html page
    # Create an Archive file containing the new files
    # Return Html to CLient with download link
    
    return JsonResponse({'message': 'Success'}, status=201)
































# Sandbox chaining Promises
@csrf_exempt
@login_required
def update_form1(request):
    print("API: update_form1")
    
    return JsonResponse({"message": "OK"},status=201)

@csrf_exempt
@login_required
def update_form2(request):
    print("API: update_form2")
    
    return JsonResponse({"message": "OK"},status=201)













@csrf_exempt
@login_required
def update_action_set(request):
    print(f"API: update_action_set()")
    
    ## Verify request method
    if(request.method != 'POST'):
        return JsonResponse({"error":"Bad request. POST method expected"}, status=301)
    
    ## Verify User Profile exists
    current_user = User.objects.get(id = request.user.id)
    user_profile_exists = User_Profile.objects.filter(user_id_fk = current_user).exists()
    if user_profile_exists:
       user_profile =  User_Profile.objects.get(user_id_fk = current_user)
    else:
        return JsonResponse({"error: User Profile Does not exist"}, status=404)
    
    # Unpack the request.POST
    user_image_set_id   = request.POST["image_set_id"]
    user_thumb_w        = request.POST['thumb_w']
    user_thumb_h        = request.POST['thumb_h']
    user_medium_w       = request.POST['medium_w']
    user_medium_h       = request.POST['medium_h']
    user_large_w        = request.POST['large_w']
    user_large_h        = request.POST['large_h']
    user_gab_chk        = request.POST['gab_chk']
    user_minds_chk      = request.POST['minds_chk']
    user_telegram_chk   = request.POST['telegram_chk']
    user_x_chk          = request.POST['x_chk']
    user_facebook_chk   = request.POST['facebook_chk']
    user_square         = request.POST['square_chk']
    user_tag_place      = request.POST['tag_placement']

    
    print(f"minds_chk = {user_minds_chk}")
    print(f"gab_chk = {user_gab_chk}")
    
    # Verify the user has uploaded an Image Set to Process ie its not the default image being submitted
    if user_image_set_id == 'default':
        return JsonResponse({"error":"Default Image Submitted. Upload an Image set to process"}, status=401)
    
    # Get the Image Set specified in the POST
    user_image_set = Image_Set.objects.get(image_set_id = user_image_set_id)

    # Check if Action_Set already exists for this Image Set
    action_set_exists = Action_Set.objects.filter(image_set_id_fk = user_image_set)
    if action_set_exists:
        # Update existing action set
        user_action_set = Action_Set.objects.get(image_set_id_fk = user_image_set)
    else:
        # Create New Action_Set for this Image_Set
        user_action_set = Action_Set.objects.create(image_set_id_fk = user_image_set)
    
    # Update New Action_Set Data
    user_action_set.thumb_w = user_thumb_w
    user_action_set.thumb_h = user_thumb_h
    user_action_set.medium_w = user_medium_w
    user_action_set.medium_h = user_medium_h
    user_action_set.large_w = user_large_w
    user_action_set.large_h = user_large_h
    
    # Update Model Boolean Fields using Python ternary operator to convert the Javascript 'true' value to python True or False: min = a if a < b else b
    user_action_set.gab_chk         = True if user_gab_chk      == 'true' else False
    user_action_set.minds_chk       = True if user_minds_chk    == 'true' else False
    user_action_set.telegram_chk    = True if user_telegram_chk == 'true' else False
    user_action_set.x_chk           = True if user_x_chk        == 'true' else False
    user_action_set.fb_chk          = True if user_facebook_chk == 'true' else False
    user_action_set.square_chk      = True if user_square       == 'true' else False
    
    # Updata tag placment
    print(f"tag placement = {user_tag_place}")
    user_action_set.tag_placement   = user_tag_place
    
    try:
        user_action_set.save()
    except:
        print(f"#### update FAIL ####")
        return JsonResponse({"error": "Internal Server Error. Database Update Failed"}, status=500)   
         
    return JsonResponse({"message": "Action Set Updated Successfully"}, status=201)





    ###########################################################################################################
    #
    # If the image has a different dimensions and height/width ratio it will cause the crop to be off
    # The greater the difference the greater the error. 
    # 
    # This can be solved by either
    # 
    # 1. Normalise the image to fit within the baseimage dimensions before processing it further.
    # 2. Scale the crop to match the image
    #
    # The easiset option is probably to scale the baseimage crop dimensions to the image being processed
    
    
    # Sketching out the normalise the image option ...
    # Scale image to the approximate size of of the image_set baseimage (the image the user chose to work with).
    # Ideally they should be the same size, but if they're not try to get them to match as best you can
    
    baseimage = Upload_File.filter(image_set_id_fk = image_set).get(baseimage = True)
    temp_pil = Image.open(baseimage.path)
    pil_baseimage = temp_pil.copy() # Ensure not messing with the original
    temp_pil.close()
    
    # Create blank pil image the same dimensions as the base image
    baseimage_h = pil_baseimage.height
    baseimage_w = pil_baseimage.width
    baseimage_template = Image.new("RGBA",(baseimage_w, baseimage_h))

    # Scale image to fit within the baseimage dimensions
    
    # Decide whwther to do the scaling based on the height or on the width
    baseimage_h2w_ratio = baseimage_h/baseimage_w               # eg 5/2 a tall rectangle               ratio: 2.5
    workimage_h2w_ratio = pil_image.height / pil_image.width    # eg 3/10 a long horizontal rectangle   ratio: 0.3
    
    # So if the baseimage is a tall vertical rectangle you would scale the width of the workimage to be the same width
    # as the base image. ie the long rectangle would be made to fit inside the tall rectangle  
    
    if baseimage_h2w_ratio > workimage_h2w_ratio:
        # scale workimage to that its width = baseimage width
        pass
    
    # Decide whwther to do the scaling based on the height or on the width
    baseimage_h2w_ratio = baseimage_h/baseimage_w               # eg 3/10 a long horizontal rectangle   ratio: 0.3
    workimage_h2w_ratio = pil_image.height / pil_image.width    # eg 5/2 a tall vertical rectangle      ratio: 2.5
    
    # If the baseimage is a long horizontal rectangle and the workimage is a tall vertical rectangle, scale the horizontal
    # height of the workimage to equal the height of the base image
    
    if baseimage_h2w_ratio < workimage_h2w_ratio:
        # Scale workimage so that the height = baseimage height
        pass
    
    # Decide whwther to do the scaling based on the height or on the width
    baseimage_h2w_ratio = baseimage_h/baseimage_w               # eg 10/7 a vertical rectangle                  ratio: 1.4
    workimage_h2w_ratio = pil_image.height / pil_image.width    # eg 9/5 a thinner, shorter vertical rectangle  ratio: 1.8
    
    # You can see that High ratio means a vertical rectangle that get thinner as the ratio goes up.
    # Here we must scale the workimage height so that it matches the baseimage height. This will leave space
    # since the workimage is thinner. This extra space can be divided and used to center the image within the baseimage template
    
    if baseimage_h2w_ratio > workimage_h2w_ratio:
        # Scale workimage so that the height = baseimage height
        scale_factor = baseimage_h/pil_image.height
        workimage_h = pil_image.height * scale_factor
        workimage_w = pil_image.width * scale_factor
    
    
    if pil_image.height > baseimage_h:
        scaled_pil_image = pil_image.resize()
    

    workimage = scale_image_to_match_master 
    
    
    
    
    
    
    
    
    
    
    
        
        
        
        
        










    #
    # The Function create_resized_images()
    # is derived from the following code which has been generalised.
    #
    
    # Create thumbnail image
    pil_thumb_image = pil_master_image
    width = user_action_set.thumb_w
    height = user_action_set.thumb_h
    print(f"height {height}")
    transformed_image = pil_thumb_image.resize((width, height))
    pil_thumb_image = transformed_image        

    # get PIL Image_name and binary data
    (pil_thumb_image_name, pil_thumb_image_data) = save_pil_image(pil_thumb_image, pil_image_name, '_thumb_', quality) 

    # Assign to ImageField
    processed_image_set.thumbnail.save(pil_thumb_image_name, ContentFile(pil_thumb_image_data))
    
    # Squarify
    if user_action_set.square_chk:   
        pil_sq_thumb_image = squarify_image(pil_thumb_image)
        
        # get PIL Image_name and binary data
        (pil_sq_thumb_image_name, pil_sq_thumb_image_data) = save_pil_image(pil_sq_thumb_image, pil_image_name, '_sq_thumb_', quality) 
        # Assign to ImageField
        processed_image_set.thumbnail_square.save(pil_sq_thumb_image_name, ContentFile(pil_sq_thumb_image_data))
        
        pil_sq_thumb_image_path = settings.MEDIA_ROOT + '/pil_images/' + pil_sq_thumb_image_name
        os.remove(pil_sq_thumb_image_path)
        pil_sq_thumb_image.close() 
        
    pil_thumb_image_path = settings.MEDIA_ROOT + '/pil_images/' + pil_thumb_image_name
    os.remove(pil_thumb_image_path)
    pil_thumb_image.close() # I think removing the image might automatically close it but this doesnt hurt either  AFAIK
    



    
    # Create Medium image
    pil_medium_image = pil_master_image
    width = user_action_set.medium_w
    height = user_action_set.medium_h
    transformed_image = pil_medium_image.resize((width, height))
    pil_medium_image = transformed_image        

    # get PIL Image_name and binary data
    (pil_medium_image_name, pil_medium_image_data) = save_pil_image(pil_medium_image, pil_image_name, '_medium_', quality) 

    # Assign to ImageField
    processed_image_set.medium.save(pil_medium_image_name, ContentFile(pil_medium_image_data))
    
    # Squarify
    if user_action_set.square_chk:   
        pil_sq_medium_image = squarify_image(pil_medium_image)
        
        # get PIL Image_name and binary data
        (pil_sq_medium_image_name, pil_sq_medium_image_data) = save_pil_image(pil_sq_medium_image, pil_image_name, '_sq_medium_', quality) 
        # Assign to ImageField
        processed_image_set.medium_square.save(pil_sq_medium_image_name, ContentFile(pil_sq_medium_image_data))
        
        pil_sq_medium_image_path = settings.MEDIA_ROOT + '/pil_images/' + pil_sq_medium_image_name
        os.remove(pil_sq_medium_image_path)
        pil_sq_medium_image.close() 
        
    pil_medium_image_path = settings.MEDIA_ROOT + '/pil_images/' + pil_medium_image_name
    os.remove(pil_medium_image_path)
    pil_medium_image.close() # I think removing the image might automatically close it but this doesnt hurt either  AFAIK
    
    
    
    #######################################################################################################
    
            
    # Create Large image
    pil_large_image = pil_master_image
    width = user_action_set.large_w
    height = user_action_set.large_h
    transformed_image = pil_large_image.resize((width, height))
    pil_large_image = transformed_image        

    # get PIL Image_name and binary data
    (pil_large_image_name, pil_large_image_data) = save_pil_image(pil_large_image, pil_image_name, '_large_', quality) 

    # Assign to ImageField
    processed_image_set.large.save(pil_large_image_name, ContentFile(pil_large_image_data))
    
    # Squarify
    if user_action_set.square_chk:   
        pil_sq_large_image = squarify_image(pil_large_image)
        
        # get PIL Image_name and binary data
        (pil_sq_large_image_name, pil_sq_large_image_data) = save_pil_image(pil_sq_large_image, pil_image_name, '_sq_large_', quality) 
        # Assign to ImageField
        processed_image_set.large_square.save(pil_sq_large_image_name, ContentFile(pil_sq_large_image_data))
        
        pil_sq_large_image_path = settings.MEDIA_ROOT + '/pil_images/' + pil_sq_large_image_name
        os.remove(pil_sq_large_image_path)
        pil_sq_large_image.close() 
        
    pil_large_image_path = settings.MEDIA_ROOT + '/pil_images/' + pil_large_image_name
    os.remove(pil_large_image_path)
    pil_large_image.close() # I think removing the image might automatically close it but this doesnt hurt either  AFAIK



    #######################################################################################################

'''
zipfile problems

    # django default_storage files 
    loc = default_storage.location
    print(f"default_storage.location = {default_storage.location}")
    base = default_storage.base_url
    print(f"default_storage.base = {default_storage.base_url}")
    file_permissions = default_storage.file_permissions_mode
    print(f"default_storage.file_permissions_mode = {default_storage.file_permissions_mode}")

        
    # (exists)
    if default_storage.exists(zip_absolute_path):
        filecheck = 'Success'
        print(f"{zip_absolute_path} exists")
    else:
        filecheck = 'Fail'
        print(f"{zip_absolute_path} doent exist")
        
    # (error) 
    # django.core.exceptions.SuspiciousFileOperation: 
    # The joined path (/zips/artVoo/imageset_31.zip) is located outside of the base path component (/home/artillery/webdev-apps/courses/CS50/Capstone/hungry_hippo/user_uploads)
    #    if default_storage.exists(image_set_zip_path):
    #        filecheck = 'Success'
    #        print(f"{image_set_zip_path} exists")
    #    else:
    #        filecheck = 'Fail'
    #        print(f"{image_set_zip_path} doent exist")
    
    # (OK) imageset_31.zip doent exist (its looking in /user_uploads/)
    if default_storage.exists(zip_short_name):
        filecheck = 'Success'
        print(f"{zip_short_name} exists")
    else:
        filecheck = 'Fail'
        print(f"{zip_short_name} doent exist")
'''



'''
def convert_nef_to_jpg_v1(input_path):
    # Open the NEF file using rawpy
    with rawpy.imread(input_path) as raw:
        # Get the RGB image data
        rgb = raw.postprocess()

        # Create a Pillow Image object from the RGB data
        image = Image.fromarray(rgb)

        # Save the image as a JPEG
        # image.save(output_path, 'JPEG')

    return image
'''



##################################################################################
#
#   convert_raw_to_jpg
#
#   When working with TemporaryUploadedFile objects from Django's request.FILES, 
#   you need to handle the file appropriately. The rawpy.imread function expects 
#   a file path or a file-like object, but a TemporaryUploadedFile is neither of 
#   those directly.
#
#   You can use io.BytesIO to create a file-like object from the content of the 
#   uploaded file.

def convert_raw_to_jpg(uploaded_file):
    # Create a path for a temporaryfile
    print(f"convert raw to jpg {uploaded_file.name}")
    
    tempraw_path = f"{settings.MEDIA_ROOT}/pil_images/{uploaded_file.name}"
    print(f"tempraw path: {tempraw_path}")
    
    # Create a file-like object from the uploaded file content (request.FILES)
    print("upload file read")
    file_content = uploaded_file.read()
    print("BytesIO")
    file_io = BytesIO(file_content)
    
    with default_storage.open(tempraw_path, 'wb') as temp_raw_dest:
        temp_raw_dest.write(uploaded_file.read())
    
    try:
        
        with Image.open(tempraw_path) as temp_raw:
               print(f"temp raw width: {temp_raw.width}")
    except Exception as e:
        print(f"RAW Error : {e}")
    

    
    # Open the file-like object using rawpy
    with rawpy.imread(temp_raw) as raw:
        # Perform demosaicing and get the RGB image data
        rgb = raw.postprocess()

        # Create a Pillow Image object from the RGB data
        image = Image.fromarray(rgb)

        # Save the image as a JPEG or do further processing as needed
        # For example, save to a BytesIO object to get the bytes
        output_io = BytesIO()
        image.save(output_io, format='JPEG')
        output_io.seek(0)

        return output_io

        
        
def is_raw_image(file_path):
    raw_extensions = ['.NEF', '.CR2', '.ARW', '.DNG']  # Add more if needed
    _, extension = os.path.splitext(file_path)
    return extension.upper() in raw_extensions




def is_an_image___always_produces_an_exception(filename):
    '''
    This might be related to how the file was being passed or the state of the file object.
    When you use the Image.open() method, it expects a file-like object. 
    The request.FILES object in Django provides a list of UploadedFile objects, 
    and each object has an associated file handle. 
    This handle might not be at the beginning of the file when you try to open it directly
    '''
    
    print(f"verifying {filename}")
    try:
        print(f"Try ...................... ")
        # try to open that image and load the data
        temp_pil = Image.open(filename)
        temp_pil.close()
        return True
    except Exception as e:
        # This will trigger everytime whether the filepassed into filename ie (request.FILES) is an image or not
        print(f"file {filename} is not an image. Error {e}")
        return False
    


# This can be solved by using BytesIO, or by opening the file using the 'with' statement

# with Image.open(BytesIO(file.read())) as img:
    # If successful, it's an image
    # return True
# BytesIO(file.read()) creates a new in-memory file-like object containing the content of the original file, 
# and Image.open() then reads from this in-memory buffer. This ensures that the file handle is positioned 
# at the start of the file content.

# Without this step, if the file handle is not at the beginning of the file, attempting to open it 
# directly with Image.open(file) might result in an exception because Pillow expects a 
# file-like object in a certain state.

# Using BytesIO helps standardize the state of the file-like object and ensures that it starts from the beginning, 
# making it suitable for reading by Image.open().

# In summary, the use of BytesIO is a common approach when dealing with libraries that expect a file-like object 
# and helps avoid potential issues with the state of the file handle


def is_an_image_without_BytesIO(filename):
    # Verify that the file is an image by opening it to check if there is an exceptioon created
    # PIL verify() method only works for PNG images apparently and otherwise returns None
    # https://github.com/python-pillow/Pillow/issues/3012#issuecomment-368219545
    
    # This works and the exception is triggered only when the file is not an image.
    # images no longer produce an exception, but its probably still better to use BytesIO

    print(f"verifying {filename}")
    try:
        print(f"Try ...................... ")
        # try to open the filename as an image
        with Image.open(filename) as img:
            print(f"image {filename} opens as image")

        return True
    except Exception as e:
        print(f"file {filename} is not an image. Error {e}")
        return False
    
# Tag Image
    # Consider the scenarios. 
    # Scenario_1: A long tag such as a url with an logo that overlays the entire height of the image
    # Scenario_2: A long tag such as a url with an logo that overlays the entire width of the image
    # Scenario_3: A logo in a rectanglular frame with height > width 
    # Scenario_4: A logo in a rectanglular frame with height < width
    # Scenario_5: A logo in a square frame with height = width
    
    # Lets say that;
    # If the ratio of height to width is 3:1 and over, its scenario_1 (long_vertical)
    # If the ratio of height to width is 1:3 and over, its scenario_2 (long_horizontal)   
    # if the ratio of height to width is 2:1, 3:2 tag is scenario_3 (short_vertical)
    # if the ratio of height to width is 1:2, 2:3 tag is scenario_4 (short_horizontal)
    # if the ratio of height to width is 1:1 tag is scenario_5 (square)
    
    # For now the app is only going to consider a tag that is a simple rectangle or square logo
    # and tags that are pasted horizontally which should cover most cases













