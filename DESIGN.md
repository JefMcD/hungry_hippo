# Hungry Hippo Design #  
**Image Batch Processor**  
**Jef McDonald Ralston**  
**18-Dec-2023**  

## Introduction ##  

Hungry Hippo Image Batch Processor is an app that allows someone to upload a folder of images and then crop, rotate, resize and tag them in an instant. This is a task often carried out to produce content for online shops, websites and for post processing dank memes by Memelords in their tireless struggle to save humanity from the forces of Evil and Tyranny.  

The Hungry Hippo app can handle all that crop rotate and tag jazz and makes it a doddle!  

For Those About To Crop.
WE SALUTE YOU!  

## CropperJS & PIL/Pillow ##
At the core of the App is the PIL/Pillow python library and the CropperJS package which are used to enable image manipulation, ultimately returning a Zipfile containing the processed images that were requested. The user can then download the zipfile, extract it and use the images as they need to. 

## Database Logical Model ##  

The app is developed on a MySQL database running on Ubuntu Linux 22.04. When the user uploads files to be processed an Image Set is created which is at the heart of the batch processing. All database entities have a One to One relationship with the Image Set table except Upload_File which is One to Many realtionship. This means that user files can be easily deleted when they logout by simply deleting their image set data which Cascades through all the other tables.

![database](/design_images/HH_Logmod-main.jpg)

## Django MEDIA ##  
The app utilizes Django’s MEDIA framework for handling images in the database and the Signals and Receivers framework to handle deleting images off the server once they have been processed and the user has logged out.

## High Level Context ##  
The App is a Single Page Application that fetches the content requested by the user whne they need it. It uses a REST API architecture, whereby there is a Javascript Client running in a Browser providing functionality to the user and fetching data from the Server using an API which queries the database and returns the required data and Html as appropriate.

![context](/design_images/Context.jpg)  

## Hungry Hippo High Level Overview ##
![design overview](/design_images/HH_DFD1_High_level.jpg)

## Uploading Images ##  
After logging in, the main features of the app are disabled until the user has uploaded a set of images to be processed. When the user clicks the Upload Images button they can browse through the folders on their device and select a folder containing images. This is then submitted through the form and the javascript client makes a fetch on the Server API to upload these files. The images are verified before being inserted into the database and an image_set id is returned along with the first image in the folder to be used as a default image to make adjustments to. 
![Uploading Images](/design_images/HH_DFD2_Upload_files.jpg)


**Upload FIles Flowchart**  
![Uploading Images Flowchart](/design_images/upload_images_flow.jpg)

## Browse Images ##  
Once the user has uploaded images to process, the rest of the app becomes available. The user can browse through the images they just uploaded to choose a different image to work with. The Hungry Hippo app will do its best to adjust any crop to fit images of different dimensions and aspect rations but for best results you should choose one which is a good general representative of the images you uploaded.
![Browse Images](/design_images/HH_DFD_Browse.jpg)

## Choose Base Image ##  
Clicking on any of the images will select it and clicking Ok will render the image in the Browser and the name of the Baseimage will be displayed
![Choose Images](/design_images/HH_DFD_Choosefile.jpg)

## Upload Tag ##
Uploading a tag for your batch is optional. Clicking on this button will allow the user to browse images on their device which will be used to tag the batch. The location of where the tag is placed is defined in the Action Set.
![Upload Tag](/design_images/HH_DFD_Upload_Tag.jpg)


## Cropping & Rotating the Image ##  
Once the user has an image loaded up into the workspace, they can rotate it, zoom in or out and set the crop size as they please.  This is tied closely to the action set and will provide the data necessary to process the images.

## Action Set ##  
The Action Set form  allows the user to define the batch process they would like to be carried out on their images. The first part allows the user to defined three sets of images for use in building a web gallery.   

![Action Set](/design_images/show_action_set_form_extended.jpg)

Here they can define a thumbnail, a medium sized image and a large image. The values presented correlate to the dimensions of the current crop dimensions. When the user enters a value in one box the other is automatically calculated to match the crop. 

The values entered by the user are also persistant, so that if they subsequently alter the crop, the values that they entered will persist and the crop values calculated accordingly. An example of how this workd is given below.  

![Action Set Update Fields](/design_images/action_set_size_input_fields.jpg)  

The remainder of the Action set allows for the user to select the quality of the images, whether or not to include images optimised for social media, or square format and the position of where the tag should go. These values are kept in the form and only sent to the API for processing when the user submits the Batch. 

## Process Batch ##  
Once the user is satisfied with the crop and has selected their options on the Action Set form they can submit the batch for processing. The Javascript client gathers all the necessary state data together with the crop data from cropperJS and the actionset data and makes an asynchronous fetch to the API, calling the Process_Batch url.  

![DFD Process Batch](/design_images/HH_DFD_Process_Batch.jpg)

On the server side the request is received and validated before unpacking the data. It then iterates through the images uploaded by the user.  For each image, the app performs the actions on the image to create a master which is then used to create all the variants requested. These processed images are stored in the database and formated into a zipfile which is returned to the user as an html link together with the name of the zipfile.

![Flow Process Batch](/design_images/process_batch.jpg)

## Create Master Image ##
At the core of the app is the process of gathering the data provided by CropperJS and the Action Set data, and then using this to apply the crop rotation and tag to a master image. This image can then be used to resize and present in different formats.

![create master image](/design_images/create_master.jpg) 

## Tag Image ##
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
![tag image](/design_images/HH_DFD_Upload_Tag.jpg) 

**Handling Images that are Similar**  
When the app is given a folder of images that are of similar width to height ratio, it can handle them without any diffculty and will crop, rotate and tag them, providing consistent images regardless of size differences.These can then be downloaded and hopefully can be used by the end user for use as web content or on social media.

**Handing Images of Different Sizes and Width to Height Ratios**  
 I wanted the app to also be able to handle a folder full of files that might be of varying dimensions and types, and for the app to at least be able to attempt producing some kind of meaningful result when faced with a chaotic situation. 

The challenge with this is that if you define a crop on an image which is a regular 2:3 portrait format, it doesnt make much sense to try to apply it to a 3:2 landscape, and the more extreme the crop and difference between the images, the less likely that the crop will provide a good result. Especially when you consider using the app on a folder on someone's phone which is likely to be a random assortment of unrelated files and images with a great diversity of size and aspect ratio.

**Solution**  
There are many ways that you could attempt to resolve this, but I chose to scale the crop in proportion to the image that it was being applied to, at least then it makes some logical sense. The only way I can think of to do this with any chance of producing good results consistently might be to use AI, wherby the app would use AI to analyse the area under the source crop and have it determine some sort of meaning/context, then scan the image being processed and find an area that seemed to be a match and compose the crop around that area. A group of faces for example. Even this might not work though when applied to a folder containing an array of unrelated and diverse content. Sounds like facial recognition software, but applied more generally. Its something that would take a bit of research to figure out but It's another puzzle for another day. 

**Width To Height Ratio (w2h ratio)**  
Many of the calculations for processing the images involve the w2h ratio of crops and images, so its worth a short note on how this works. (I know its high school maths but who carries that kind of stuff around in their head?) Throughout the app the w2h ratio is used. Never the h2w ratio (which would reverse all the calculations)

**w2h ratio = 1**  Width and height are the same size aka, a square  
**w2h ratio < 1**   Width is less than the height. aka Portrait. The closer the ratio is to 0 the longer and narrower the rectangle gets. eg values like 0.8 is a squarish rectangle  0.1 is a long narrow portrait  
**w2h ratio > 1**   Width is greater than the height aka Landscape. The higher the value the longer and narrower the landscape is. Values like 1.5 is a regular landscape, 10 is a wide panoramma etc 
![scaling](/design_images/scaling.jpg) 


**Adapt, Scale, Normalize**  
The following explains the logic behind how the Adapt and Scale crop works, which is used in the normalization process to handle images with varying dimensions. This is carried out when creating the master image before they're sent for resizing.  

![adapt & scale](/design_images/adapt_scale_crop.jpg) 

**Normalization**
![Normalization](/design_images/scale_crop2.jpg)


## Resize Images ##  
The main work of the app is done within the Create Master function. Once this master has been created and its stored in the database, it is then available to be resized in whatever format the user has asked for. Each of the selections made in the Action Set are now processed and a set of processed imaged are created for, thumbnails, medium and large images as well as any of the other options selected.  

![Resize Images](/design_images/resize_image.jpg)



## Create Zipfile ##
Once the processed images are in the database the app then iterates through them and creates a Zip archive to hold them in. This is them saved to the database and a download link is rendered on the server and returned to the client. This is then displayed in the Browser and the User can download it and extact the files they reequested.

![Get Zip Archive](/design_images/get_zip_archive.jpg)


## Logging Out ## 

Finally when the user logs out the app will delete any image sets created by the user and all the database entitities related to it. Using Django’s signal and receiver framework the action of deleting an instance is used to automatically delete the image files from the server to keep it clean.Only the user profile and the user data will remain.

![Cascade Delete](/design_images/cascade_delete.jpg)






