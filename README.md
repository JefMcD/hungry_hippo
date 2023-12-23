 # Hungry Hippo
 **Image Batch Processing App**  
Hungry Hipp is an app which allows a user to quicky crop, rotate and tag images that can then be used as content for websites and social media. This is a regular task for small independent shops, artitst and crafters, for example a music shop, an artist or a cake maker that needs to photograph their items for sale and then upload the pictures to their website.  
 
Often, to save time, the pictures can be made by setting up a small studio area in the corner of the room with a camera on a tripod, automatically taking pictures of one item after another with the same background, composition and lighting. All you have to do is swap one item out for the next and let the camera roll.

Once this is complete, the next step is to crop the images, get it centered properly, tag it and produce all the various image sizes you need for the website. This is where the Hungry Hippo App can save hours and hours of work and headache. (Believe me, I know, Ive been there!)

Other uses could be for processing images for timelapse videos or for cropping and tagging memes.

## Project Pre-requisites    
**The project must be sufficiently distinct from previous projects and be more complex.**  

**What the App Doesn't Do**  
The project is not an e-commerce or social network app  
The project is not based on the previous CS50 Pizza Shop project  

**What the App Does Do**

**MEDIA**  
This project explores Django's framework for handling images and user uploads. This is a feature which hasnt been a requirementf any previous project on the course although I began to explore it in the Network project. This adds a significant amount of complexity to the project since it requires great deal of additional configuration and handling. This additional complexity is across the board, affecting the settings, urls, views, models and forms, so the ability for Django to handle binary media is a major upgrade. In implementing this, care also needs to be taken to avoid allowing hackers to use the file upload feature to give them access to your server as this can be a potential entry point.   

**Pillow**  
The project will explore the python PIL package for manipulating and processing images, and handling their interfaces between Django request.FILES, PIL images, ImageFields and handling them as Binary objects.

Official Website  
https://pypi.org/project/Pillow/  
https://pillow.readthedocs.io/en/stable/reference/index.html  
Tutorial  
https://www.youtube.com/watch?v=5QR-dG68eNE  


**MySQL**  
The project will use a small relational database to store and process user's images by configuring Django to use MySQL.  


**Node Package Manager NPM**  
The app will explore the use of package libraries available from npm. This takes this project to the next level since this is an essential part of modern web development. Specifically the app will import and make use of the package library  cropper.js which provides methods for image manipulation in the browser and returns data that can be used by Pillow to create the images needed.     
https://github.com/fengyuanchen/cropperjs#getting-started  
https://fengyuanchen.github.io/cropperjs/  
  
Other packages that provide similar libraries that were considered  
https://www.cssscript.com/touch-drag-rotate-resize-subjx/  
https://www.cssscript.com/minimal-resizable-rotatable/  
https://www.cssscript.com/draggable-resizable-rotatable-plugin/  



## Requirements  
The primary requirement of this app is to be able to batch process a folder of images, crop, rotate and create a set of thumbnails, a set of medium sized images and a set of large images that can be used on a website.  
1. A user must register and login to use the app

2. A set of images is provided to the app via a file upload button

3. The User will be able to Browse through the images uploaded and select which one to work with

4. The User will be able to upload a tag for their images

5. The user will define the following alterations to be applied to each image  
- Crop
- Resize
- Rotation

6. The User will be able to define a set of actions to perform on the images
- humnail Size. Height and Width   
- Medium Size. Height and Width  
- Large Size. Height and Width  
If a width or height is supplied the other is calculated to keep the aspect ratio

- The user can define a size optimized for social media posts
- The user can choose A square format option where the image will be inside a square 
(for instagram for example)
- Be able to define the quality/filesize of the resulting images
- The can define the placement of the uploaded tag 

7. The App will then produce a Zipfile with the requested images and provide a download link.


## Secondary Requirement
A secondary requirement of the app is that it can handle a folder containing random files and process them in some reasonable manner.   

Translating a crop which is specific to an individual image to a folder of unrelated images which have different sizes and dimensions doesnt make any sense and is unlikely to produce any meaningful or usable result. So in tackling this problem I tried to make the App at least able to identify which files were images and exclude non-images. Frrom there I decided that the best way forward was to process them in a way that is at least logical. So the app filters out all the non-images in the folder and can be used for making general cropping tasks like removing borders from around images. I think that in general the result is fairly reasonable.








