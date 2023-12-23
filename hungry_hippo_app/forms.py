

from django import forms
from django.utils.safestring import mark_safe

####################################################################
#
# Upload Multiple Files at once
# https://docs.djangoproject.com/en/4.2/topics/http/file-uploads/
# https://docs.djangoproject.com/en/4.2/ref/forms/fields/#imagefield
# 
####################################################################

# Define Custom Widget that Inherits from the default ClearableFileInput widget
class MultipleImageInput(forms.ClearableFileInput):
    allow_multiple_selected = True

# Define Custom Form Input with custom widget form multiple image uploads
class MultipleImageField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleImageInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

# Create the New Form Input
class Source_Folder_Form(forms.Form):
    source_images = MultipleImageField(label = '',  required=True,
                                 widget = MultipleImageInput(
                                    attrs={
                                    'class': 'general-form-input',
                                    'id': 'source-folder-input',
                                    'webkitdirectory': True,
                                    'directory': True,
                                    'multiple': True,
                                    }
                                 ))
    
    
   
# Tag Image Upload Form 
class Tag_Upload_Form(forms.Form):
   tag_upload = forms.ImageField(label = '',  required=True,
                                 widget = forms.ClearableFileInput(
                                    attrs={
                                    'class': 'general-form-input',
                                    'id': 'tag-form-input'
                                    }
                                 ))
   
   
   
class Action_Set_Image_Widths(forms.Form):
   # This produces a <div> containing an INPUT and a LABEL
   thumbnail_width   = forms.IntegerField(label = 'Thumb', initial=250,  required=False,
                                 widget = forms.NumberInput(
                                    attrs={
                                    'class': 'action-set-resize-input',
                                    'id': 'thumb-width-input',

                                    }
                                 ))
   
   # Others follow suit accordingly
   medium_width   = forms.IntegerField(label = 'Medium', initial=1000,  required=False,
                                 widget = forms.NumberInput(
                                    attrs={
                                    'class': 'action-set-resize-input',
                                    'id': 'medium-width-input',

                                    }
                                 ))
        
   large_width   = forms.IntegerField(label = 'Large', initial=1500,  required=False,
                                 widget = forms.NumberInput(
                                    attrs={
                                    'class': 'action-set-resize-input',
                                    'id': 'large-width-input',
  
                                    }
                                 ))
   
   
class Action_Set_Image_Heights(forms.Form):
   # This produces a <div> containing only an INPUT
   thumbnail_height   = forms.IntegerField(label = '', initial=1000,  required=False,
                                 widget = forms.NumberInput(
                                    attrs={
                                    'class': 'action-set-resize-input',
                                    'id': 'thumb-height-input',
  
                                    }
                                 ))
   
   medium_height   = forms.IntegerField(label = '', initial=1000,  required=False,
                                 widget = forms.NumberInput(
                                    attrs={
                                    'class': 'action-set-resize-input',
                                    'id': 'medium-height-input',
  
                                    }
                                 ))
        
   large_height   = forms.IntegerField(label = '', initial=1500,  required=False,
                                 widget = forms.NumberInput(
                                    attrs={
                                    'class': 'action-set-resize-input',
                                    'id': 'large-height-input',

                                    }
                                 ))
   
   
class Tag_Position_Form(forms.Form):
   tag_placement = [('center','Center'),('top_left', 'Top Left'),('top_right','Top Right'),('lower_left', 'Low Left'),('lower_right', 'Low Right'),('no_tag', 'No Tag')]
   tag_placement_choice =  forms.ChoiceField(label = '',
                     widget=forms.RadioSelect(
                        attrs={
                           'class': 'tag-placement-input',
                           'id': 'tag-placement-radio_btns',
                        }
                     ), choices = tag_placement)
   

    
    
''' 
####################################################################################################################
###
###     Creating a Custom Widget
###
###     This is to create a Custom Widget for the checkboxes so that the Label appears as an Icon instead of text
###
####################################################################################################################
    
## FAIL
# Each Checkbox that has an Icon instead of a Label requires a custome widget to render their Icon
#. It seems that the 'id' attribute is not always present in the attrs dictionary. FAIL
class ImageCheckboxWidget_Fail(forms.CheckboxInput):
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        img_tag = '<img class="checkbox-img" src="{% static \'hungry_hippo_app/images/sm_icons/white/gab.svg\' %}">'
        label = '<label class="checkbox-label" for="{}">{}</label>'.format(attrs['id'], img_tag)
        
        return mark_safe(label + html)
    
    
    
# Each Checkbox that has an Icon instead of a Label requires a custome widget to render their Icon
# you need to use the 'get' method to retrieve the 'id' attribute:
# Also its important to Note that you cant reference static data from outside of the html template.
# static data needs to be within a template for it to be rendered by the Djano static data engine
# 
class ImageCheckboxWidget(forms.CheckboxInput):
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        img_tag = '<img class="checkbox-img" src="">'
        label = '<label class="checkbox-label" for="{}">{}</label>'.format(attrs.get('id', ''), img_tag)

        
        return mark_safe(label + html)
    
    
    
    
    

class SMedia1_Form_test(forms.Form):
    chk1 = forms.BooleanField(
        label='chk1',
        initial=False,
        required=False,
        widget=ImageCheckboxWidget(attrs={'class': 'checkbox-form-input', 'id': 'gab-checkbox-input'})
    )


class SMedia1_Form(forms.Form):

    gab         = forms.BooleanField(label = '', initial=False,  required=False,
                                 widget = ImageCheckboxWidget(
                                    attrs={
                                    'class': 'checkbox-form-input',
                                    'id': 'gab-checkbox-input',
                                    'name': 'gab-checkbox',
                                    }
                                 ))
    
    minds       = forms.BooleanField(label = '', initial=False,  required=False,
                                 widget = forms.CheckboxInput(
                                    attrs={
                                    'class': 'checkbox-form-input',
                                    'id': 'minds-checkbox-input'
                                    }
                                 ))
    telegram    = forms.BooleanField(label = '', initial=False,  required=False,
                                 widget = forms.CheckboxInput(
                                    attrs={
                                    'class': 'checkbox-form-input',
                                    'id': 'telegram-checkbox-input'
                                    }
                                 ))
    x           = forms.BooleanField(label = '', initial=False,  required=False,
                                 widget = forms.CheckboxInput(
                                    attrs={
                                    'class': 'checkbox-form-input',
                                    'id': 'x-checkbox-input'
                                    }
                                 ))
    parler      = forms.BooleanField(label = '', initial=False,  required=False,
                                 widget = forms.CheckboxInput(
                                    attrs={
                                    'class': 'checkbox-form-input',
                                    'id': 'parler-checkbox-input'
                                    }
                                 ))


class SMedia2_Form(forms.Form):

    gettr       = forms.BooleanField(label = 'Gettr', initial=False,  required=False,
                                 widget = forms.CheckboxInput(
                                    attrs={
                                    'class': 'checkbox-form-input',
                                    'id': 'gettr-checkbox-input',
                                    'size': 10,
                                    }
                                 ))
    instagram   = forms.BooleanField(label = 'Instagram', initial=False,  required=False,
                                 widget = forms.CheckboxInput(
                                    attrs={
                                    'class': 'checkbox-form-input',
                                    'id': 'instagram-checkbox-input'
                                    }
                                 ))
    substack    = forms.BooleanField(label = 'Substack', initial=False,  required=False,
                                 widget = forms.CheckboxInput(
                                    attrs={
                                    'class': 'checkbox-form-input',
                                    'id': 'substack-checkbox-input'
                                    }
                                 ))
    facebook    = forms.BooleanField(label = 'Facebook', initial=False,  required=False,
                                 widget = forms.CheckboxInput(
                                    attrs={
                                    'class': 'checkbox-form-input',
                                    'id': 'facebook-checkbox-input'
                                    }
                                 ))
    redpill     = forms.BooleanField(label = 'Redpill', initial=False,  required=False,
                                 widget = forms.CheckboxInput(
                                    attrs={
                                    'class': 'checkbox-form-input',
                                    'id': 'redpill-checkbox-input'
                                    }
                                 ))
    
    
    
# Single Image Upload Form 
class Image_Upload_Form(forms.Form):
   image_upload = forms.ImageField(label = '',  required=True,
                                 widget = forms.ClearableFileInput(
                                    attrs={
                                    'class': 'general-form-input',
                                    'id': 'image-upload-input'
                                    }
                                 ))



    


 '''      
       