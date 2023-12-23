




function show_tag_form(){
    console.log("#### Function: show_tag_form ####")

    // Select Image Form Block and Set its Style to Display
    const image_browser_element = document.querySelector('#image-browser-block')
    const source_form_element = document.querySelector('#source-folder-form')
    const action_set_form_element = document.querySelector('#action-set-block')
    const tag_form_element = document.querySelector('#tag-form-block')
    if(tag_form_element.style.display == 'block'){
        tag_form_element.style.display = 'none'
        image_browser_element.style.display = 'none'
        source_form_element.style.display = 'none'
        action_set_form_element.style.display = 'none'
    }else{
        tag_form_element.style.display = 'block'
        image_browser_element.style.display = 'none'
        source_form_element.style.display = 'none'
        action_set_form_element.style.display = 'none'
    }
    return
}







////////////////////////////////////////////////////////////////////////////
/*                                                                        */
/*    Submit Tag Image  Form                                              */
/*                                                                        */
////////////////////////////////////////////////////////////////////////////
function submit_tag_form(){
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
        
        let path = `upload_tag/${image_set_id}` // app path
        //let path = `analyse_imageFile_Vs_PILFile/${image_set_id}` // figuring out how images work

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

                // Get Tag Image 
                const infopanel_tagname = document.getElementById('tag-name')
                infopanel_tagname.innerHTML = result.tagname
                console.log("tagname = ", result.tagname)
                const  tag_thumb = document.getElementById("tag-thumb")
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















