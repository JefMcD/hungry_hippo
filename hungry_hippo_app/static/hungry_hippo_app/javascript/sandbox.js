











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

    console.log("crop width: ", crop_width)
    console.log("crop height: ", crop_height)
    console.log("large scale: ", scale_factor)
    console.log("h_val: ", large_h_val)

    document.getElementById('large-height-input').value = Math.round(large_h_val)

    // track persistance values
    large_height_is_persistant = false
    large_width_is_persistant  = true
    persistant_large_h = 0
    persistant_large_w = large_w_val

    return
}

function update_large_w(){
    // When a User enters a value into the Height box
    // This function updates the largenail Width value in ratio to the crop 
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

    console.log("crop width: ", crop_width)
    console.log("crop height: ", crop_height)
    console.log("large scale: ", scale_factor)
    console.log("h_val: ", large_h_val)

    document.getElementById('large-width-input').value = Math.round(large_w_val)

    // User has entered a height value which is now the persistant value
    large_height_is_persistant = true
    large_width_is_persistant  = false
    persistant_large_h = large_h_val
    persistant_large_w = 0

    return
}



















function update_action_set_model(){
    console.log('update_action_set_model()')
    return new Promise((resolve, reject) => {
            // This function can be called either by the action_set_form eventListener or from outside the form by the finalise function
            // Get Actiom Set Form 'Resize' Elements
            let thumb_width_input = document.getElementById('thumb-width-input')
            let thumb_height_input = document.getElementById('thumb-height-input')
            let medium_width_input = document.getElementById('medium-width-input')
            let medium_height_input = document.getElementById('medium-height-input')
            let large_width_input = document.getElementById('large-width-input')
            let large_height_input = document.getElementById('large-height-input')

            // Get  Actiom Set Form 'Social Media' Checkbox elements
            let gab_chk_input = document.getElementById('gab-checkbox-input')
            let minds_chk_input = document.getElementById('minds-checkbox-input')
            let telegram_chk_input = document.getElementById('telegram-checkbox-input')
            let x_chk_input = document.getElementById('x-checkbox-input')
            let facebook_chk_input = document.getElementById('facebook-checkbox-input')

            // Get  Actiom Set Form, 'Format checkbox elements
            let square_format_input = document.getElementById('square-format-input')

            // Update the State Data for the form resize values that have changed
            gab_chk         = gab_chk_input.checked
            minds_chk       = minds_chk_input.checked
            telegram_chk    = telegram_chk_input.checked
            x_chk           = x_chk_input.checked
            facebook_chk    = facebook_chk_input.checked

            square_format = square_format_input.checked

            // Build Form Data
            let action_set_form = new FormData()
            action_set_form.append('thumb_w', thumb_width_input.value)
            action_set_form.append('thumb_h', thumb_height_input.value)
            action_set_form.append('medium_w', medium_width_input.value)
            action_set_form.append('medium_h', medium_height_input.value)
            action_set_form.append('large_w', large_width_input.value)
            action_set_form.append('large_h', large_height_input.value)

            action_set_form.append('gab_chk', gab_chk)
            action_set_form.append('minds_chk', minds_chk)
            action_set_form.append('telegram_chk', telegram_chk)
            action_set_form.append('x_chk', x_chk)
            action_set_form.append('facebook_chk', facebook_chk)
            action_set_form.append('square_chk', square_format)

            action_set_form.append('image_set_id', image_set_id)


            // Asynchronous Fetch 'POST' the Form data into the Action_Set Model.
            fetch('/update_action_set', {
                method: "POST",
                body: action_set_form
            })
            .then(response => {
                response_status = response.status
                return response.json()
            })
            .then(result => {
                if(response_status == 201){
                    display_user_message(result.message, response_status)
                }else{
                    display_user_message(result.error, response_status)
                }
        
                close_action_set_form()
            })
            .catch((error) => {
                error = "ERROR returned: "+ error
                display_user_message(error, response_status)

            }) // End Fetch
        })
}











///////////////////////////////////////////////////
/*                                               */
/*    Submit Tag Image  Form                     */
/*                                               */
///////////////////////////////////////////////////
function submit_tag_form_debugging(){
    console.log('### FUNCTION: submit_tag_form() ###')

    document.querySelector('#tag-form').onsubmit = function() {

        const tag_form_input = document.querySelector('#tag-form-input');

        // Create a FormData object to store the data from the form
        // When this is sent via the fetch it becomes request.POST and request.FILES
        // const form_data = new FormData();

        // if form is not empty copy contents of form into form_data else return
        if (tag_form_input.value){
            var form_data = new FormData(document.getElementById('tag-form'));
        }else{
            console.log('########## calling close_form #################')
            close_tag_form()
            return false
        }

        // Fetch POST to API path API Path
        
        // let path = `upload_tag/${image_set_id}` // app path
        let path = `analyse_imageFile_Vs_PILFile/${image_set_id}` // figuring out how images work

        fetch(path,{
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
                console.log("tag uploaded")

                // Get Pil Image Data
                let pil_bands      = result.pil_bands
                let pil_image_name = result.pil_image_name
                document.getElementById("pil-data1").innerHTML = pil_bands
                document.getElementById("pil-data2").innerHTML = pil_image_name

                // Get Django Image Data
                django_tag_name_div = document.getElementById("django-name")
                django_tag_path_div = document.getElementById("django-path")
                django_tag_url_div = document.getElementById("django-url")

                django_tag_name_div.innerHTML = result.django_tag_name
                django_tag_path_div.innerHTML = result.django_tag_path
                django_tag_url_div.innerHTML  = result.django_tag_url


                // Get Tag Image 
                tag_area = document.getElementById('tag-area')
                console.log('tagname = ', result.tagname)
                tag_area.innerHTML = result.django_tag_name
                tag_thumb = document.getElementById("tag-thumb")
                tag_thumb.src = result.django_tag_url
            }else{
                console.log('Error Updating Profile ' + result.message)
            }
        })
        .catch((error) => {
            error = "Error Loading Image => " + error
            display_user_message(error, response_status)

        })

        close_tag_form()

        return false // prevent form from calling an action such as sending the form to another page
    }
}










































/*//////////////////////////////////////////////////////////////////////////////////////


Chaning two Asynchronous Processes so that one will execute when another finishes


*///////////////////////////////////////////////////////////////////////////////////////
function process1() {
    return new Promise((resolve, reject) => {

            let form1 = new FormData()
            form1.append('form1_value', 100)

            fetch('/update_form1', {
                method: "POST",
                body: form1
            })
            .then(response => {
                response_status = response.status
                return response.json()
            })
            .then(result => {
                console.log("success");
                resolve(); // Resolve the promise when process1 is complete
            })
            .catch((error) => {
                error = "ERROR returned: " + error
                display_user_message(error, response_status)
                reject(error); // Reject the promise if there is an error
            });

    });
}

function process2() {
    return new Promise((resolve, reject) => {
 
            let form2 = new FormData()
            form2.append('form2_value', 200)

            fetch('/update_form2', {
                method: "POST",
                body: form2
            })
            .then(response => {
                response_status = response.status
                return response.json()
            })
            .then(result => {
                console.log("success");
                resolve(); // Resolve the promise when process2 is complete
            })
            .catch((error) => {
                error = "ERROR returned: " + error
                display_user_message(error, response_status)
                reject(error); // Reject the promise if there is an error
            });

    });
}

// Usage
function finalise(){
    // Follows the same structure as a Fetch
    process1()
    .then(() => {
        return process2(); // Return the promise from process2
    })
    .then(() => {
        console.log("Both processes completed");
    })
    .catch(error => {
        console.error("Error:", error);
    });
}





    // this was the example of how to iterate throgh the radio buttons found around the web (repeatedly), but doesnt work here for some reason
    /*
    let radio_element = ''
    for(radio_element in image_browse_radios){
        if(radio_element.checked){
            console.log('found checked')
            workimage_url = radio_element.values
            break;
        }else{
            console.log('no radio checked')
        }
    }


                console.log("Trying alternative")
    let radio_element = ''
    for(radio_element in tag_radio_choices){
        if(radio_element.checked){
            console.log('found checked', radio_element)
            //tag_placement_choice = radio_element.values
            break;
        }else{
            console.log('no radio checked')
        }
    }
            */
