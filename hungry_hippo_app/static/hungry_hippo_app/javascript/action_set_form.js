//////////////////////////////////////////////////////////////////////////////////////////////////////////////
//
// Cropper. The objects used by Cropperjs to manipulate the image in the Browser
// const image = document.getElementById('cropper-image') // Browser Element containing the image being manipulated
// var image_crop      // This is the Cropperjs Object used to manipulate the image

// var cropper_data    // A Dictionary Object containing Cropper Data cropper_data = image_crop.getData({rounded: true})
/*
    x: the offset left of the cropped area
    y: the offset top of the cropped area
    width: the width of the cropped area
    height: the height of the cropped area
    rotate: the rotated degrees of the image
    scaleX: the scaling factor to apply on the abscissa of the image if scaled
    scaleY: the scaling factor to apply on the ordinate of the image if scaled
*/

// var image_base_data // A Dictionary Object containing the Cropper data about the original image image_base_data = image_crop.getImageData({rounded: true})
/*
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
*/



// Image_Set. The id of the Image_Set associated with the files uploaded and being processed
// var image_set_id = 'no images uploaded'
//
///////////////////////////////////////////////////////////////////////////////////////////////////////////////



// Default Sizes for the image resies
var thumbsize_default = 250
var mediumsize_default = 1000
var largesize_default = 1500

// Keep track of persistant values
var thumb_height_is_persistant = false
var thumb_width_is_persistant = false
var persistant_thumb_h = 0
var persistant_thumb_w = 0

var medium_height_is_persistant = false
var medium_width_is_persistant = false
var persistant_medium_h = 0
var persistant_medium_w = 0

var large_height_is_persistant = false
var large_width_is_persistant = false
var persistant_large_h = 0
var persistant_large_w = 0

// Default Image Scale Factor
var scale_factor = 1
var med_scale = 1
var large_scale = 1

// Action Set. State Data. The default user choices for the checkboxes
var gab_chk = ''
var minds_chk = ''
var telegram_chk = ''
var x_chk = ''
var fb_chk = ''

var square_chk = ''
var background_chk = ''
var banner_chk = ''


function reset_action_set_form(){
        console.log("reset_action_set_data()")
        // This function returns an object literal containing the values held in the action set form
        const thumb_width_input = document.getElementById('thumb-width-input')
        const thumb_height_input = document.getElementById('thumb-height-input')
        const medium_width_input = document.getElementById('medium-width-input')
        const medium_height_input = document.getElementById('medium-height-input')
        const large_width_input = document.getElementById('large-width-input')
        const large_height_input = document.getElementById('large-height-input')
        const quality_slider = document.getElementById('quality-slider-input')
        
    
        // Get  Actiom Set Form 'Social Media' Checkbox elements
        const gab_chk_input = document.getElementById('gab-checkbox-input')
        const minds_chk_input = document.getElementById('minds-checkbox-input')
        const telegram_chk_input = document.getElementById('telegram-checkbox-input')
        const x_chk_input = document.getElementById('x-checkbox-input')
        const facebook_chk_input = document.getElementById('facebook-checkbox-input')
    
        // Get  Actiom Set Form, 'Format checkbox elements
        const square_format_input = document.getElementById('square-format-input')

        // Get the Base Image Data and Cropper Data
        image_base_data = image_crop.getImageData({rounded: true})
        cropper_data = image_crop.getData({rounded: true})

        // Default Sizes for the image resies
        thumbsize_default = 250
        mediumsize_default = 1000
        largesize_default = 1500

        // Keep track of persistant values
        thumb_height_is_persistant = false
        thumb_width_is_persistant = true
        persistant_thumb_h = thumbsize_default
        persistant_thumb_w = thumbsize_default

        medium_height_is_persistant = false
        medium_width_is_persistant = true
        persistant_medium_h = mediumsize_default
        persistant_medium_w = mediumsize_default

        large_height_is_persistant = false
        large_width_is_persistant = true
        persistant_large_h = largesize_default
        persistant_large_w = largesize_default

        // Default Image Scale Factor
        scale_factor = 1
        med_scale = 1
        large_scale = 1

        // Action Set. State Data. The default user choices for the checkboxes
        gab_chk = ''
        minds_chk = ''
        telegram_chk = ''
        x_chk = ''
        fb_chk = ''

        square_chk = ''
        background_chk = ''
        banner_chk = ''
        
        // Set Values to defaults
        init_thumb_size_inputs()
        init_medium_size_inputs()
        init_large_size_inputs()
    
        // Reset Quality SLider
        quality_slider.value = 70


}



function init_thumb_size_inputs(){
    console.log("#########################################################init thumb size")
    // Get Crop Height & Width Values for the Action Set Form
    let thumb_w_value = document.getElementById('thumb-width-input').value
    let thumb_h_value = document.getElementById('thumb-height-input').value

    let cropper_data = image_crop.getData({rounded: true})
    let image_data   = image_crop.getCanvasData()


    // Calculate New Input Field Values 
    // These are based on the Crop Data
    // The persistant value is the last value (height or width) entered by the user into a field
    // This value is used to work out the other fields value in ratio to the crop
    if (thumb_height_is_persistant){
        // User has recently specified a thumbnail height
        thumb_h_value = persistant_thumb_h
        scale_factor  = thumb_h_value / cropper_data.height
        thumb_w_value = cropper_data.width * scale_factor
    }else if (thumb_width_is_persistant){
        // User Has recently specified a thumbnail width
        thumb_w_value = persistant_thumb_w
        scale_factor = thumb_w_value / cropper_data.width
        thumb_h_value = cropper_data.height * scale_factor
    }else{
        // Initial Default Settings
        console.log("setting thumb width default")
        scale_factor = 1
        thumb_w_value = 250
        thumb_h_value = 250
    }

    document.getElementById('thumb-width-input').value = Math.trunc(thumb_w_value)
    document.getElementById('thumb-height-input').value = Math.trunc(thumb_h_value)


    console.log("thumb_w = ", thumb_w_value)
    console.log("thumb_h = ", thumb_h_value)
}



function init_medium_size_inputs(){
    // Get Crop Height & Width Values for the Action Set Form
    let medium_w_value = document.getElementById('medium-width-input').value
    let medium_h_value = document.getElementById('medium-height-input').value


    // Calculate New Input Field Values 
    // These are based on the Crop Data
    // The persistant value is the last value (height or width) entered by the user into a field
    // This value is used to work out the other fields value in ratio to the crop
    if (medium_height_is_persistant){
        // User has recently specified a mediumnail height
        medium_h_value = persistant_medium_h
        scale_factor  = medium_h_value / cropper_data.height
        medium_w_value = cropper_data.width * scale_factor
    }else if (medium_width_is_persistant){
        // User Has recently specified a mediumnail width
        medium_w_value = persistant_medium_w
        scale_factor = medium_w_value / cropper_data.width
        medium_h_value = cropper_data.height * scale_factor
    }else{
        // Initial Default Settings
        scale_factor = 1
        medium_w_value = 500
        medium_h_value = 500
    }
    document.getElementById('medium-width-input').value = Math.trunc(medium_w_value)
    document.getElementById('medium-height-input').value = Math.trunc(medium_h_value)
}


function init_large_size_inputs(){
    // Get Crop Height & Width Values for the Action Set Form
    let large_w_value = document.getElementById('large-width-input').value
    let large_h_value = document.getElementById('large-height-input').value


    // Calculate New Input Field Values 
    // These are based on the Crop Data
    // The persistant value is the last value (height or width) entered by the user into a field
    // This value is used to work out the other fields value in ratio to the crop
    if (large_height_is_persistant){
        // User has recently specified a largenail height
        large_h_value = persistant_large_h
        scale_factor  = large_h_value / cropper_data.height
        large_w_value = cropper_data.width * scale_factor
    }else if (large_width_is_persistant){
        // User Has recently specified a largenail width
        large_w_value = persistant_large_w
        scale_factor = large_w_value / cropper_data.width
        large_h_value = cropper_data.height * scale_factor
    }else{
        // Initial Default Settings
        scale_factor = 1
        large_w_value = 1000
        large_h_value = 1000
    }
    document.getElementById('large-width-input').value = Math.trunc(large_w_value)
    document.getElementById('large-height-input').value = Math.trunc(large_h_value)
}






/******************************************************************************* */
/*
/*    Handle Image Upload Form
/*
/******************************************************************************** */
function show_action_set_form(){
    console.log("#################### Function: show_action_set_form #################################")


    // Select Action Set Form Block and Set its Style to Display
    const image_browser_element = document.querySelector('#image-browser-block')
    const source_form_element = document.querySelector('#source-folder-form')
    const action_set_form_element = document.querySelector('#action-set-block')
    const tag_form_element = document.querySelector('#tag-form-block')
    if(action_set_form_element.style.display == 'block'){
        image_browser_element.style.display = 'none'
        source_form_element.style.display = 'none'
        action_set_form_element.style.display = 'none'
        tag_form_element.style.display ='none'
    }else{
        image_browser_element.style.display = 'none'
        source_form_element.style.display = 'none'
        action_set_form_element.style.display = 'block'
        tag_form_element.style.display ='none'
    }


    // Insert the cropper data into the Resize fields
    //console.log("thumb scale = ", scale_factor)
    //document.getElementById('thumb-width-input').value = cropper_data.width * scale_factor
    //document.getElementById('thumb-height-input').value = cropper_data.height * scale_factor

    //console.log("Opening Form width = ", cropper_data.width)
    //console.log("Opening Form heigtht = ", cropper_data.height)

    //document.getElementById('medium-width-input').value = cropper_data.width
    //document.getElementById('medium-height-input').value = cropper_data.height


    // Get the Base Image Data and Cropper Data
    image_base_data = image_crop.getImageData({rounded: true})
    cropper_data = image_crop.getData({rounded: true})
    
    // Whenever the Action Set form is loaded, the size input fields are initialised. 
    // The values will depend on which fields have persistant values which are used to calculate the crop dimensions
    init_thumb_size_inputs()
    init_medium_size_inputs()
    init_large_size_inputs()



    //const play_btn_a = document.getElementById('play-btn')
    //console.log(' Exiting Show Action_set_form: Play btn => ', play_btn_a)
    return
}







function get_action_set_data(){
    console.log("get_action_set_data()")
    // This function returns an object literal containing the values held in the action set form
    const thumb_width_input = document.getElementById('thumb-width-input')
    const thumb_height_input = document.getElementById('thumb-height-input')
    const medium_width_input = document.getElementById('medium-width-input')
    const medium_height_input = document.getElementById('medium-height-input')
    const large_width_input = document.getElementById('large-width-input')
    const large_height_input = document.getElementById('large-height-input')

    // Get quality Slider element
    const quality_slider = document.getElementById('quality-slider-input')

    // Get  Actiom Set Form 'Social Media' Checkbox elements
    const gab_chk_input = document.getElementById('gab-checkbox-input')
    const minds_chk_input = document.getElementById('minds-checkbox-input')
    const telegram_chk_input = document.getElementById('telegram-checkbox-input')
    const x_chk_input = document.getElementById('x-checkbox-input')
    const facebook_chk_input = document.getElementById('facebook-checkbox-input')

    // Get  Actiom Set Form, 'Format checkbox elements
    const square_format_input = document.getElementById('square-format-input')

    // Update the State Data for the form resize values that have changed
    gab_chk         = gab_chk_input.checked
    minds_chk       = minds_chk_input.checked
    telegram_chk    = telegram_chk_input.checked
    x_chk           = x_chk_input.checked
    facebook_chk    = facebook_chk_input.checked

    square_format = square_format_input.checked


    // Get Tag Placement
    console.log("Getting Tag Data")
    let tag_radio_choices = document.getElementsByClassName('tag-placement-input')
    let tag_placement_choice = '5'
    nodeList = tag_radio_choices
    console.log("iterating through node list")
    for (let index = 0; index < nodeList.length; index++) {
        //console.log(nodeList[index]);
        //console.log(nodeList[index].checked)
        //console.log(nodeList[index].value)

        if(nodeList[index].checked){
            tag_placement_choice = nodeList[index].value
        }
    }
    console.log("tag placement = ", tag_placement_choice)

    let action_set_data = {
        "thumb_w": thumb_width_input.value,
        "thumb_h": thumb_height_input.value,
        "medium_w": medium_width_input.value,
        "medium_h": medium_height_input.value,
        "large_w": large_width_input.value,
        "large_h": large_height_input.value,
    
        "quality_val": quality_slider.value,

        "gab_chk": gab_chk,
        "minds_chk": minds_chk,
        "telegram_chk": telegram_chk,
        "x_chk": x_chk,
        "fb_chk": facebook_chk,
        "square_chk": square_format,
        'tag_placement': tag_placement_choice,
    
        "image_set_id": image_set_id,
    }

    return action_set_data
}












function submit_action_set_form(){
    console.log('Javascript: submit_action_set_form')
    console.log('scale_factor = ', scale_factor)

    document.getElementById('action_set_form').onsubmit = function() {
        close_action_set_form()
        return false
    } 
} 








function update_thumb_h(){
    // When a User enters a value into the Width box
    // This function updates the thumbnail Height value in ratio to the crop dimensions 
    console.log("update_thumb_h()")


    // Get Input Width Value
    let thumb_w_val = document.getElementById('thumb-width-input').value
    console.log('thumb width = ', thumb_w_val)

    let crop_width = cropper_data.width
    let crop_height = cropper_data.height


    scale_factor = thumb_w_val / crop_width

    let thumb_h_val = crop_height * scale_factor


    document.getElementById('thumb-height-input').value = Math.trunc(thumb_h_val)

    // track persistance values
    thumb_height_is_persistant = false
    thumb_width_is_persistant  = true
    persistant_thumb_h = 0
    persistant_thumb_w = thumb_w_val

    // Show persistant field in the form
    const thumb_h_input = document.getElementById('thumb-height-input')
    thumb_h_input.classList.remove('persistant')
    const thumb_w_input = document.getElementById('thumb-width-input')
    thumb_w_input.classList.add('persistant')

    return
}

function update_thumb_w(){
    // When a User enters a value into the Height box
    // This function updates the thumbnail Width value in ratio to the crop 
    console.log("update_thumb_w()")
    // scale = user_value / known value
    // new_w = crop_w * scale

    // Get the Height entered by the User and calculate the width according to the crop scale ratio
    let thumb_h_val = document.getElementById('thumb-height-input').value

    // Get Cropper width & Height
    let crop_width = cropper_data.width
    let crop_height = cropper_data.height

    // Calculate Scale Factor: This is the Ratio of the Input Value to the Crop Value
    scale_factor = thumb_h_val / crop_height

    let thumb_w_val = crop_width * scale_factor

    document.getElementById('thumb-width-input').value = Math.trunc(thumb_w_val)

    // User has entered a height value which is now the persistant value
    thumb_height_is_persistant = true
    thumb_width_is_persistant  = false
    persistant_thumb_h = thumb_h_val
    persistant_thumb_w = 0

    // Show persistant field in the form
    const thumb_h_input = document.getElementById('thumb-height-input')
    thumb_h_input.classList.add('persistant')
    const thumb_w_input = document.getElementById('thumb-width-input')
    thumb_w_input.classList.remove('persistant')


    return
}




function update_medium_h(){
    // When a User enters a value into the Width box
    // This function updates the mediumnail Height value in ratio to the crop dimensions 
    console.log("update_medium_h()")


    // Get Input Width Value
    let medium_w_val = document.getElementById('medium-width-input').value
    console.log('medium width = ', medium_w_val)

    let crop_width = cropper_data.width
    let crop_height = cropper_data.height


    scale_factor = medium_w_val / crop_width

    let medium_h_val = crop_height * scale_factor

    document.getElementById('medium-height-input').value = Math.trunc(medium_h_val)

    // track persistance values
    medium_height_is_persistant = false
    medium_width_is_persistant  = true
    persistant_medium_h = 0
    persistant_medium_w = medium_w_val

    // Show persistant field in the form
    const medium_h_input = document.getElementById('medium-height-input')
    medium_h_input.classList.remove('persistant')
    const medium_w_input = document.getElementById('medium-width-input')
    medium_w_input.classList.add('persistant')


    return
}

function update_medium_w(){
    // When a User enters a value into the Height box
    // This function updates the mediumnail Width value in ratio to the crop 
    console.log("update_medium_w()")
    // scale = user_value / known value
    // new_w = crop_w * scale

    // Get the Height entered by the User and calculate the width according to the crop scale ratio
    let medium_h_val = document.getElementById('medium-height-input').value

    // Get Cropper width & Height
    let crop_width = cropper_data.width
    let crop_height = cropper_data.height

    // Calculate Scale Factor: This is the Ratio of the Input Value to the Crop Value
    scale_factor = medium_h_val / crop_height

    let medium_w_val = crop_width * scale_factor


    document.getElementById('medium-width-input').value = Math.trunc(medium_w_val)

    // User has entered a height value which is now the persistant value
    medium_height_is_persistant = true
    medium_width_is_persistant  = false
    persistant_medium_h = medium_h_val
    persistant_medium_w = 0

    // Show persistant field in the form
    const medium_h_input = document.getElementById('medium-height-input')
    medium_h_input.classList.add('persistant')
    const medium_w_input = document.getElementById('medium-width-input')
    medium_w_input.classList.remove('persistant')


    return
}










function update_large_h(){
    // When a User enters a value into the Width box
    // This function updates the largenail Height value in ratio to the crop dimensions 
    console.log("update_large_h()")


    // Get Input Width Value
    let large_w_val = document.getElementById('large-width-input').value
    console.log('large width = ', large_w_val)

    let crop_width = cropper_data.width
    let crop_height = cropper_data.height


    scale_factor = large_w_val / crop_width

    let large_h_val = crop_height * scale_factor

    document.getElementById('large-height-input').value = Math.trunc(large_h_val)

    // track persistance values
    large_height_is_persistant = false
    large_width_is_persistant  = true
    persistant_large_h = 0
    persistant_large_w = large_w_val

    // Show persistant field in the form
    const large_h_input = document.getElementById('large-height-input')
    large_h_input.classList.remove('persistant')
    const large_w_input = document.getElementById('large-width-input')
    large_w_input.classList.add('persistant')


    return
}

function update_large_w(){
    // When a User enters a value into the Height box
    // This function updates the large Width value in ratio to the crop 
    console.log("update_large_w()")
    // scale = user_value / known value
    // new_w = crop_w * scale

    // Get the Height entered by the User and calculate the width according to the crop scale ratio
    let large_h_val = document.getElementById('large-height-input').value

    // Get Cropper width & Height
    let crop_width = cropper_data.width
    let crop_height = cropper_data.height

    // Calculate Scale Factor: This is the Ratio of the Input Value to the Crop Value
    scale_factor = large_h_val / crop_height

    let large_w_val = crop_width * scale_factor

    document.getElementById('large-width-input').value = Math.trunc(large_w_val)

    // User has entered a height value which is now the persistant value
    large_height_is_persistant = true
    large_width_is_persistant  = false
    persistant_large_h = large_h_val
    persistant_large_w = 0

    // Show persistant field in the form
    const large_h_input = document.getElementById('large-height-input')
    large_h_input.classList.add('persistant')
    const large_w_input = document.getElementById('large-width-input')
    large_w_input.classList.remove('persistant')


    return
}



function add_quality_slider_event_listener(){
    const quality_slider = document.getElementById('quality-slider-input')
    const quality_value = document.getElementById('image-quality-value')
    
    quality_slider.oninput = function() {
        qv = this.value
        quality_value.innerHTML = qv
    } 

}



















function add_image_resize_input_event_listeners(){
    // When the user inserts a value into the width update the height according to the crop dimensions
    const thumb_w = document.getElementById('thumb-width-input')
    thumb_w.addEventListener('keyup', update_thumb_h)

    // When the user inserts a value into the height update the width according to the crop dimsnsions
    const thumb_h = document.getElementById('thumb-height-input')
    thumb_h.addEventListener('keyup', update_thumb_w)

    const medium_w = document.getElementById('medium-width-input')
    medium_w.addEventListener('keyup', update_medium_h)
    
    const medium_h = document.getElementById('medium-height-input')
    medium_h.addEventListener('keyup', update_medium_w)

    const large_w = document.getElementById('large-width-input')
    large_w.addEventListener('keyup', update_large_h)
    
    const large_h = document.getElementById('large-height-input')
    large_h.addEventListener('keyup', update_large_w)

}




function close_action_set_form(){
    const form_block = document.getElementById('action-set-block')
    form_block.style.display = 'none'
    return
}



