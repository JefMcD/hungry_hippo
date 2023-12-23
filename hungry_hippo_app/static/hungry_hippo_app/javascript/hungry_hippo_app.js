


/******************************************************************************* */
/*
/*    State Data, Global Variables
/*
/******************************************************************************** */

// Cropper DataElement. The area in the Browser for Display the Crop Data
const crop_box_x_offset   = document.getElementById('crop-box-x-offset')
const crop_box_y_offset   = document.getElementById('crop-box-y-offset')
const crop_box_width      = document.getElementById('crop-box-width')
const crop_box_height     = document.getElementById('crop-box-height')
const crop_box_rotation   = document.getElementById('crop-box-rotation')



// Cropper. The objects used by Cropperjs to manipulate the image in the Browser
const image = document.getElementById('cropper-image') // Browser Element containing the image being manipulated
var image_crop      // This is the Cropperjs Object used to manipulate the image

// Image_Set. The id of the Image_Set associated with the files uploaded and being processed
var image_set_id = 'no images uploaded'

// The Id of the image used to do the crop/rotate/resize
var baseimage_id = ''


/******************************************************************** 
 * 
 *  Display User Message
 * 
*********************************************************************/
function display_user_message(msg, response_status){
    let message = ''
    if (response_status == 201){
        message = "HIPPO SMILEY FACE: " + msg
        console.log(message)
    }else{
        message = "HIPPO FROWNY FACE: " + msg
        console.log(message, response_status)

    }
}

function get_image_shortname(filename){
    //  return the filenmae from the image_filename ie '/path/myfile.jpg' returns 'myfile'
    // IT DOESNT RETURN THE FORWARD SLASH. The forward slash causes path traversal errors
    
    // Python version
    // pattern = r'([^/]+)$'
    // match = re.search(pattern, image_filename)
    // if match:
    //    filename = match.group()

    const shortname = filename.match(/\/([^\/]+)$/)[1];

    return shortname
}

/******************************************************************** 
 * 
 *  Load Image Into Cropper
 * 
*********************************************************************/
function load_image_for_cropper(image_url){
    // Using Globals Variables, image, image_crop and cropper_data
    console.log("Jason Returned => " + image_url)
    image.src = image_url

    // Destroy Existing Image Crop 
    if(image_crop){
        image_crop.destroy()
        image_crop = null
    }
    // Create New Cropper for image_url
    console.log('######### New Cropper ############')
    image_crop = new Cropper(image, {
        aspectRatio: 0,
        viewMode: 1,
        dragMode: 'move',
        background: false,
    })

    // get cropper_data for the Image and the crop
    cropper_data = image_crop.getData({rounded: true})
    image_base_data =  image_crop.getImageData({rounded: true})

    if(cropper_data){
        console.log('cropper_data = ', cropper_data)
        //display_cropper_data()
    }

}


/******************************************************************************* */
/*
/*    Handle Source Folder Form
/*
/******************************************************************************** */
function show_source_form(){
    console.log('#### Function: show_folder_form ####')
    console.log('Folder click')
    // Select Form Block and Set its Style to Display
    const source_form_element = document.querySelector('#source-folder-form')
    const image_browser_element = document.querySelector('#image-browser-block')
    const action_set_form_element = document.querySelector('#action-set-block')
    const tag_form_element = document.querySelector('#tag-form-block')

    if(source_form_element.style.display == 'block'){
        source_form_element.style.display = 'none'
        image_browser_element.style.display = 'none'
        action_set_form_element.style.display = 'none'
        tag_form_element.style.display ='none'
    }else{
        source_form_element.style.display = 'block'
        image_browser_element.style.display = 'none'
        action_set_form_element.style.display = 'none'
        tag_form_element.style.display ='none'
    }
    return
}


/**************************************************************************** */
/*                                                                            */
/*    Submit Source Folder Images                                             */
/*                                                                            */
/**************************************************************************** */
function upload_images_folder(){
    console.log('### FUNCTION: upload_images_folder() ###')

    document.querySelector('#source-form').onsubmit = function() {
            // Clear the tag fields on the UI
            document.getElementById('tag-name').innerHTML = 'No Tag Uploaded'
            document.getElementById('tag-thumb').src = ''

            const source_folder_input = document.querySelector('#source-folder-input');
            // image_list = image_folder_input.files; // Get the list of files.

            // Create a FormData object to store the dataafrom the form
            // When this is sent via the fetch it becomes request.POST and request.FILES
            // const form_data = new FormData();

            // if form is not empty copy contents of form into form_data else return
            if (source_folder_input.value){
                var form_data = new FormData(document.getElementById('source-form'));
            }else{
                console.log('########## calling close_form #################')
                close_source_form()
                return false
            }

            // Fetch POST to API path API Path
            console.log('fetch /upload_images_folder')
            fetch('/upload_images_folder',{
                method: "POST",
                body: form_data
            })
            .then(response => {
                response_status =  response.status
                return response.json()
            })
            .then(result => {      
                if(response_status === 201){
                    // Upload Successfull
                    load_image_for_cropper(result.image_file)

                    // Get image_set_id
                    image_set_id = result.image_set_id

                    // Get Base Image Id
                    baseimage_id = result.baseimage_id

                    // Display Image Set Id
                    image_set_id_element = document.getElementById('download-link')
                    image_set_id_element.innerHTML = "Working on Image Set " + result.image_set_id
                    console.log('image_set_id = ', image_set_id)

                    // Display Baseimage Name
                    baseimage_name = document.getElementById('baseimage-name')
                    baseimage_name.innerHTML = result.baseimage_name

                }else{
                    display_user_message(result.error, response_status)
                }

                // enable Play Button
                const play_btn = document.getElementById('play-btn')
                play_btn.addEventListener('click', process_batch)
                play_btn.classList.add('active') 
                play_btn.classList.remove('disable')


                //enable select workimage button
                const image_btn = document.getElementById('image-btn')
                image_btn.addEventListener('click', show_image_browse_form)
                image_btn.classList.add('active')
                image_btn.classList.remove('disable')

                // enable tag button
                const tag_btn = document.getElementById('tag-btn')
                tag_btn.addEventListener('click', show_tag_form)
                tag_btn.classList.add('active')
                tag_btn.classList.remove('disable')

            })
            .catch((error) => {
                error = "Error Loading Images => "+error
                display_user_message(error, response_status)
            })

            close_source_form()

            return false // prevent form from calling an action such as sending the form to another page
    }
}







/******************************************************************************* */
/*
/*    Show Image Browser Form
/*
/******************************************************************************** */
function show_image_browse_form(){
    console.log("#### Function: show_image_form ####")

    let path = `get_browse_images/${image_set_id}`
    // Fetch images from the Server and load them into the form
    console.log(`Fetching Path ${path}`)
    fetch(path, {
        method: 'GET'
    })
    .then(response => {
        response_status = response.status
        return response.json()
    })
    .then( result => {
        if(response_status == 201){
            display_user_message(result.message, response_status)
            console.log("handling get_browse_images result")

            // Insert the resturned Html containing the uploaded images into the form
            user_image_uploads = document.getElementById('user-image-uploads')
            user_image_uploads.innerHTML = result.images_html

            // Select Image Form Block and Set its Style to Display
            console.log('getting form elements')
            const image_browser_element = document.querySelector('#image-browser-block')
            const source_form_element = document.querySelector('#source-folder-form')
            const action_set_form_element = document.querySelector('#action-set-block')
            const tag_form_element = document.querySelector('#tag-form-block')
            if(image_browser_element.style.display == 'block'){
                console.log("setting all forms off")
                image_browser_element.style.display = 'none'
                source_form_element.style.display = 'none'
                action_set_form_element.style.display = 'none'
                tag_form_element.style.display ='none'
            }else{
                console.log("setting image browser element")
                image_browser_element.style.display = 'block'
                source_form_element.style.display = 'none'
                action_set_form_element.style.display = 'none'
                tag_form_element.style.display ='none'
            }
        }else{
            display_user_message(result.error, response_status)
        }
    })
    .catch( error => {
        display_user_message(error, response_status)

    })
    console.log('Images Fetched and Browse form Displayed')
    console.log('Returning. Ajax complete')
    return
}



//////////////////////////////////////////////
/*                                          */
/*    Submit Browse Image                   */
/*                                          */
//////////////////////////////////////////////
function submit_browse_image_form(){
    console.log('### FUNCTION: submit_browse_image_form() ###')

    document.querySelector('#image-browser-form').onsubmit = function() {

            // get cropper workimage
            const baseimage_div = document.getElementById('cropper-image')
            let baseimage_url = baseimage_div.src

            // get selected radio element
            const image_browse_radios = document.querySelectorAll(".gallery-browser-input")
            console.log(`image_browse_radios => ${image_browse_radios}`)

            // This is how to iterate throgh the radio buttons. The examples given online were all bollox
            let nodeList = image_browse_radios
            let baseimage_name = ''
            let image_selected = false
            for (var index = 0; index < nodeList.length; index++) {
  
                if(nodeList[index].checked){
                    baseimage_url = nodeList[index].value
                    baseimage_id = nodeList[index].id
                    baseimage_name = nodeList[index].dataset.imagename
                    image_selected = true
                }
            }

            if (image_selected){
                // set src of workImage to selected image
                baseimage_div.src = baseimage_url

                // update Base image name
                const baseimage_name_div = document.getElementById('baseimage-name')
                shortname = get_image_shortname(baseimage_name)
                baseimage_name_div.innerHTML = shortname

                // Destroy Default Cropper (image_crop Globale Variable)
                image_crop.destroy()
                image_crop = null

                // Create New Cropper, create new image_crop after destroying the default one
                cropperize_baseimage()

            }

            close_browse_image_form()
            
            return false // prevent form from calling an action such as sending the form to another page
    }
}












function close_browse_image_form(){
    // form_block is the outermost parent div containing all the form sub-divs
    // form_input is the input fields of the form. These should all be cleared when the form is closed unless you want them to persist
    form_block = document.getElementById('image-browser-block')
    //form_input = Its a radio selection block of images so leave it selected

    form_block.style.display = 'none'
    //form_input.value = ''
    return
}

function close_image_form(){
    form_block = document.getElementById('image-browser-block')
    form_input = document.getElementById('image-upload-input')

    form_block.style.display = 'none'
    form_input.value = ''
    return
}

function close_tag_form(){
    form_block = document.getElementById('tag-form-block')
    form_input = document.getElementById('tag-form-input')

    form_block.style.display = 'none'
    form_input.value = ''
    return
}

function close_source_form(){
    form_block = document.getElementById('source-folder-form')
    form_input = document.getElementById('source-folder-input')

    form_block.style.display = 'none'
    form_input.value = ''
    return
}












  /******************************************************************************* */
  /*
  /*    Handle Cropperjs
  /*
  /******************************************************************************** */
function restore_workimage(){
    console.log('setData')
    restore_data = {
        x: cropper_data.x,
        y: cropper_data.y,
        width: cropper_data.width,
        height: cropper_data.height,
        rotate: cropper_data.rotate,
    }

    image_crop.crop()
    image_crop.setData(restore_data)

   // Enable Hide Button
   //hide_btn = document.getElementById('hide-btn')
   //hide_btn.addEventListener('click', hide_crop)
   //hide_btn.classList.remove('disable')
   //hide_btn.classList.add('active')

    //display_cropper_data()
}

function cropperize_baseimage(){

    console.log('###### cropperize_baseimage #########')
    // If Cropper Image already Exist reset it 
    if (image_crop){
        // Cropper already active.
        image_crop.reset()
    }else{
        // Create Cropper
        image_crop = new Cropper(image, {
            aspectRatio: 0,
            viewMode: 1,
            dragMode: 'move',
            background: false,
        })


        //display_cropper_data()
        /*
        cropper_data = image_crop.getData()
        if(cropper_data){
            console.log('cropper_data = ', cropper_data)
            //display_cropper_data()
        }
        */
    }

    return
}


function hide_crop(){
    console.log('######### Destroy Cropper ############')
    // store cropper_data and clear the crop
    console.log('cropper_data: ', cropper_data)
    cropper_data = image_crop.getData()
    image_crop.clear()

    // Disable Hide Button
    //hide_btn = document.getElementById('hide-btn')
    //hide_btn.removeEventListener('click', hide_crop)
    //hide_btn.classList.add('disable')
    //hide_btn.classList.remove('active')
  

    // Display cropper data in the UI
    //display_cropper_data()
    return
}

function update_cropper_data(){
    cropper_data = image_crop.getData({rounded: true})
    image_base_data = image_crop.getCanvasData({rounded:true})
    console.log("base_data.width => ", image_base_data.width)
    return
}





function process_batch(){
    console.log('### process_batch ####')  

        // Get latest Crop data
        let cropper_data = image_crop.getData({rounded:true})
        let action_set_data = get_action_set_data()
        
        batch_data = {
            'image_set_id': image_set_id,
            'baseimage_id': baseimage_id,
            'cropper_data':{
                'crop_x_offset' : cropper_data.x,
                'crop_y_offset' : cropper_data.y,
                'crop_width'    : cropper_data.width,
                'crop_height'   : cropper_data.height,
                'crop_scale_x'  : cropper_data.scaleX,
                'crop_scale_y'  : cropper_data.scaleY, 
                'image_rotation': cropper_data.rotate,
            },
            'action_set_data': action_set_data
        }

        fetch('/process_batch',{
            method: "PUT",
            body: JSON.stringify(batch_data)
        })
        .then(response => {
            response_status = response.status
            return response.json()
        })
        .then(processed_data => {
            if(response_status == 201){
                console.log('Javascript: API PUT returned Success')
                processed_gallery = processed_data.gallery_html

                display_user_message(processed_gallery, response_status)
                //console.log("zipfile: ",processed_data.zipfile_html_link)

                const zip_download_link = document.getElementById('download-link')
                zip_download_link.innerHTML=processed_data.zipfile_html_link

                const infopanel_zipname = document.getElementById('zip-name')
                infopanel_zipname.innerHTML = processed_data.zipname

            }else if(response_status == 400){
                display_user_message(processed_data.message, response_status )
            }else if(response_status == 401){
                display_user_message(processed_data.error, response_status)
            }
        })
        .catch(error => {
        display_user_message(error, '000')
        }) // End Fetch

        return
}





























































function add_buttons(){
    console.log('#### add_buttons ####')

    // Add Listeners to the Source Folder Form
    const source_folder_btn = document.getElementById('source-btn')
    source_folder_btn.addEventListener('click', show_source_form)

    // Add Listeners to the Close and Submit buttons
    const source_form_cancel = document.getElementById('source-form-cancel')
    source_form_cancel.addEventListener('click', close_source_form)

    const source_form_submit = document.getElementById('source-form-submit')
    source_form_submit.addEventListener('click', upload_images_folder)


    // Add Listeners to the Single Image Upload Form
    const image_btn = document.getElementById('image-btn')
    //image_btn.addEventListener('click', show_image_browse_form)
    // Initially Disable the Image Upload btn until the Source Folder has been chosen 
    //image_btn.classList.add('disable')
    //image_btn.classList.remove('active')

    // Add Listeners to the Close and Submit buttons
    const image_upload_cancel = document.getElementById('browse-image-form-cancel')
    image_upload_cancel.addEventListener('click', close_browse_image_form)

    const image_upload_submit = document.getElementById('browse-image-form-submit')
    image_upload_submit.addEventListener('click', submit_browse_image_form)


    // Add Listeners to the Tag Image Upload Form
    const tag_btn = document.getElementById('tag-btn')
    //tag_btn.addEventListener('click', show_tag_form)
    // Initially Disable the Tag Upload btn until the Source Folder has been chosen 
    //tag_btn.classList.add('disable')
    //tag_btn.classList.remove('active')

    // Add Listeners to the Close and Submit buttons
    const tag_upload_cancel = document.getElementById('tag-form-cancel')
    tag_upload_cancel.addEventListener('click', close_tag_form)

    const tag_upload_submit = document.getElementById('tag-form-submit')
    tag_upload_submit.addEventListener('click', submit_tag_form)

    // Add Listeners to the Select Action Set Button
    const action_set_btn = document.getElementById('action-set-btn')
    action_set_btn.addEventListener('click', show_action_set_form)

    const action_set_cancel_btn = document.getElementById('close-action-set-form')
    action_set_cancel_btn.addEventListener('click', close_action_set_form)


    // It might be good to have an option to resize without a crop .. but not just yet

    // Add Listeners to the Crop Button
    // const crop_btn = document.getElementById('crop-btn')
    // crop_btn.addEventListener('click', cropperize_baseimage)

    // Add Listeners to the Hide Button
    // const close_btn = document.getElementById('hide-btn')
    // close_btn.addEventListener('click', hide_crop)

    // Add Listeners to the Restore Crop Button
    // const setData_btn = document.getElementById('setData-btn')
    // setData_btn.addEventListener('click', restore_workimage)

    //const action_set_submit_btn = document.getElementById('submit_action_set_form')
    //action_set_submit_btn.addEventListener('click', submit_action_set_form)

}


function load_cropper_image(){
    const slider = document.getElementById("slider-range");
   // const slider_value = document.getElementById("slider-value");
   // const cropper_rotation = document.getElementById("crop-box-rotation")

    var rotation = 0
    cropperize_baseimage()
   // slider_value.innerHTML = 0; // Display the default slider value
   // cropper_rotation.innerHTML = 0

    update_cropper_data()

    // Add Slider oninput listener and Update the current slider value (each time you drag the slider handle)
    slider.oninput = function() {
        //slider_value.innerHTML = this.value;
        // The delta is the change on the slider position. 
        // A move to the right will produce a positive value and a clockwise rotation and a move to the left a nagative value and a counter-clockwise rotation
        delta = this.value - rotation
        image_crop.rotate(delta)

        // Update the current rotation position
        rotation = this.value

        // get cropper rotation data
        cropper_data = image_crop.getData()
        //display_cropper_data()
        //cropper_rotation.innerHTML = cropper_data.rotate
    } 
}


/*********************************************************************** */
/*
/* Main Javascript Function on DOM Content Loaded
/*
/*
/*********************************************************************** */
document.addEventListener('DOMContentLoaded', function() {
    console.log('#############################################################################')
    console.log('################################## Reload ###################################')
    console.log('#############################################################################')  
    // addEventListeners to the Appropriate Buttons on the Profile
    add_buttons()
    add_image_resize_input_event_listeners()
    add_quality_slider_event_listener()
    load_cropper_image()
    reset_action_set_form()




});




/******************************************************************************* */
/*
/*    Cropper Data for reference
/*
/******************************************************************************** */
/*
https://www.npmjs.com/package/cropperjs
https://fengyuanchen.github.io/cropperjs/

// A Dictionary Object containing Cropper Data cropper_data = image_crop.getData({rounded: true})

var cropper_data  = {
    x: the offset left of the cropped area
    y: the offset top of the cropped area
    width: the width of the cropped area
    height: the height of the cropped area
    rotate: the rotated degrees of the image
    scaleX: the scaling factor to apply on the abscissa of the image if scaled
    scaleY: the scaling factor to apply on the ordinate of the image if scaled
}

function display_cropper_data(){
    //crop_box_x_offset.innerHTML = cropper_data.x
    //crop_box_y_offset.innerHTML = cropper_data.y
    //crop_box_width.innerHTML = cropper_data.width
    //crop_box_height.innerHTML = cropper_data.height
    //crop_box_rotation.innerHTML = cropper_data.rotate
    return
}


// A Dictionary Object containing the Cropper data about the original 
// image image_base_data = image_crop.getImageData({rounded: true})

var image_base_data = {
    left: the offset left of the image
    top: the offset top of the image
    width: the width of the image
    height: the height of the image
    naturalWidth: the natural width of the image
    naturalHeight: the natural height of the image
    aspectRatio: the aspect ratio of the image
    rotate: the rotated degrees of the image if it is rotated
    scaleX: the scaling factor to apply on the abscissa of the image if scaled
    scaleY: the scaling factor to apply on the ordinate of the image if scaled
}

*/












