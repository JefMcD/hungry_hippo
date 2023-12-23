


// This could probably be implemented by iterating over an object instead of having a function for each input
let resize_images_widget = {
    thumb_sizes : {
        width_id: "thumb_width_input",
        height_id: "thumb_height_input",
        persistance: false,
        persistance_value: 0 
    },

    medium_sizes: {
        width_id: "medium_width_input",
        height_id: "medium_height_input",
        persistance: false,
        persistance_value: 0 
    },

    large_sizes: {
        width_id: "large_width_input",
        height_id: "large_height_input",
        persistance: false,
        persistance_value: 0 
    }


}
var MainObj = {

    prop1: "prop1MainObj",
    
    Obj1: {
      prop1: "prop1Obj1",
      prop2: "prop2Obj1",    
      Obj2: {
        prop1: "hey you",
        prop2: "prop2Obj2"
      }
    },
      
    Obj3: {
      prop1: "prop1Obj3",
      prop2: "prop2Obj3"
    },
    
    Obj4: {
      prop1: true,
      prop2: 3
    }  
  };
  
  console.log(MainObj.Obj1.Obj2.prop1);







function init_large_size_inputs(){
    // Get Form Height & Width Values
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
        // Initial Settings
        scale_factor = 1
        large_w_value = cropper_data.width
        large_h_value = cropper_data.height
    }
    let scaled_large_w = Math.round(cropper_data.width * scale_factor)
    let scaled_large_h = Math.round(cropper_data.height * scale_factor)
    document.getElementById('large-width-input').value = scaled_large_w
    document.getElementById('large-height-input').value = scaled_large_h
}