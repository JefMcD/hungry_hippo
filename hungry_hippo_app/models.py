from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q, Deferrable, UniqueConstraint
from django.db.models.signals import pre_delete, post_delete
from django.dispatch.dispatcher import receiver
from django.conf import settings
import os

# Create your models here.


class User(AbstractUser):
    def __str__(self):
        return f"{self.pk}, {self.username}, {self.email}"


class User_Profile(models.Model):
    # Therefore the django uses the MEDIA_URL as the base path for the upload_to
    # Define Model Fields
    user_profile_id     = models.AutoField(primary_key=True, db_index=True, db_column='user_profile_id')
    user_id_fk          = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_profile_set', db_column='user_id_fk')
    user_profile_folder = models.CharField(null=True, blank=True,  max_length=150, db_column='user_profile_folder')

    # Define how class will be represented in Django Admin Screens
    def __str__(self):
        return f"user_profile_id = {self.user_profile_id}, user_id_fk = {self.user_id_fk}"
    

class Image_Set(models.Model):
    image_set_id            = models.AutoField(primary_key=True, db_index=True, db_column='image_set_id')
    user_profile_id_fk      = models.OneToOneField(User_Profile, on_delete=models.CASCADE, related_name='image_sets', db_column='user_profile_id_fk')


    

class Upload_File(models.Model):
    image_set_files = 'image_set_files'
    max_name_length = 512
    
    file_id         = models.AutoField(primary_key=True, db_index=True, db_column='file_id')
    image_set_id_fk = models.ForeignKey(Image_Set, on_delete=models.CASCADE, related_name='upload_file_set', db_column='image_set_id_fk')
    image_file      = models.ImageField(null = False, blank=False, upload_to=image_set_files, max_length=max_name_length, db_column='image_file')  
    baseimage        = models.BooleanField(default = False, db_column='baseimage')  
    

    
    def serialize(self):
        return {
            'image_file': self.image_file.url
        }

class Processed_Images(models.Model):
    processed_folder = 'processed_images'
    processed_folder_absolute_path = settings.MEDIA_ROOT + '/processed_images'
    thumbnail_folder = 'processed_images/thumbnail'
    medium_folder = 'processed_images/medium'
    large_folder = 'processed_images/large'
    soc_med_folder = 'processed_images/social_media'
    sq_soc_med_folder = 'processed_images/social_media'
    sq_thumbnail_folder = 'processed_images/sq_thumbnail'
    sq_medium_folder = 'processed_images/sq_medium'
    sq_large_folder = 'processed_images/sq_large'
    
    max_name_length = 512
    processed_images_id = models.AutoField(primary_key=True, db_index=True, db_column='processed_images_id')
    upload_file_fk      = models.OneToOneField(Upload_File, on_delete=models.CASCADE, related_name='processed_images_set', db_column='upload_file_fk')
    
    master              = models.ImageField(null=False, blank=False, upload_to=processed_folder, max_length=max_name_length, db_column='master' )
    
    thumbnail           = models.ImageField(null=False, blank=False, upload_to=thumbnail_folder, max_length=max_name_length,    db_column='thumbnail' )
    thumbnail_square    = models.ImageField(null=False, blank=False, upload_to=sq_thumbnail_folder, max_length=max_name_length, db_column='thumbnail_square' )
    medium              = models.ImageField(null=False, blank=False, upload_to=medium_folder, max_length=max_name_length,       db_column='medium' )
    medium_square       = models.ImageField(null=False, blank=False, upload_to=sq_medium_folder, max_length=max_name_length,    db_column='medium_square' )
    large               = models.ImageField(null=False, blank=False, upload_to=large_folder, max_length=max_name_length,        db_column='large' )
    large_square        = models.ImageField(null=False, blank=False, upload_to=sq_large_folder, max_length=max_name_length,     db_column='large_square' )
    social_media        = models.ImageField(null=False, blank=False, upload_to=soc_med_folder, max_length=max_name_length,      db_column='social_media' )
    social_media_square = models.ImageField(null=False, blank=False, upload_to=sq_soc_med_folder, max_length=max_name_length,   db_column='social_media_square' )



    def folder_location(self):
        return self.processed_folder_absolute_path
    

class Action_Set(models.Model):
    actions_set_id      = models.AutoField(primary_key=True, db_index=True, db_column='action_set_id')
    name                = models.CharField(null=False, blank=False, default='action_set', max_length=45, db_column='name')
    image_set_id_fk     = models.OneToOneField(Image_Set, on_delete=models.CASCADE, related_name = 'action_sets', db_column='image_set_id_fk')
 
    thumb_w          = models.IntegerField(null = True, blank = True, default=250,  db_column='thumb_w')
    thumb_h          = models.IntegerField(null = True, blank = True, default=250,  db_column='thumb_h')
    medium_w         = models.IntegerField(null = True, blank = True, default=1000, db_column='medium_w')
    medium_h         = models.IntegerField(null = True, blank = True, default=1000, db_column='medium_h')
    large_w          = models.IntegerField(null = True, blank = True, default=1500, db_column='large_w')
    large_h          = models.IntegerField(null = True, blank = True, default=1500, db_column='large_h')
    
    img_qual         = models.IntegerField(default=70, db_column='img_qual')
 
    gab_chk             = models.BooleanField(null = True, blank = True, default=False, db_column='gab_chk')
    minds_chk           = models.BooleanField(null = True, blank = True, default=False, db_column='minds_chk')
    telegram_chk        = models.BooleanField(null = True, blank = True, default=False, db_column='telegram_chk')
    x_chk               = models.BooleanField(null = True, blank = True, default=False, db_column='x_chk')
    fb_chk              = models.BooleanField(null = True, blank = True, default=False, db_column='fb_chk')
    soc_med_chk         = models.BooleanField(null = True, blank = True, default=False, db_column='soc_med_chk')
    square_chk          = models.BooleanField(null = True, blank = True, default=False, db_column='square_chk')
    
    tag_placement       = models.CharField(null = True, blank = True, default='no_tag', max_length=16, db_column='tag_placement')


class Imagetag(models.Model):
    user_image_tags = 'user_tags'
    max_name_length = 512
    imagetag_id         = models.AutoField(primary_key=True, db_index=True, db_column='imagetag_id')
    image_set_id_fk     = models. OneToOneField(Image_Set, on_delete=models.CASCADE, related_name='imagetag_sets', db_column='image_set_id_fk')
    tag                 = models.ImageField(null=True, blank=True, upload_to=user_image_tags,max_length=max_name_length, db_column='tag')



class Zipfile_Download(models.Model):
    zip_folder = 'zipfiles'
    zipfile_id          = models.AutoField(primary_key=True, db_index=True, db_column='zipfile_id')
    image_set_id_fk     = models.OneToOneField(Image_Set, on_delete=models.CASCADE, related_name='zipfile_download', null=True, blank=True, db_column='image_set_id_fk')
    zipfile             = models.FileField(null=True, upload_to=zip_folder, blank=True, db_column='zipfile')
     
 
    

class PIL_Cropper(models.Model):
    pil_crop_id         = models.AutoField(primary_key=True, db_index=True, db_column='pil_crop_id')
    image_set_id_fk     = models. OneToOneField(Image_Set, on_delete=models.CASCADE, related_name='PIL_Cropper_sets', db_column='image_set_id_fk')
    pil_crop_left       = models.IntegerField(null = True, blank = True, db_column='pil_crop_left')
    pil_crop_upper      = models.IntegerField(null = True, blank = True, db_column='pil_crop_upper')
    pil_crop_right      = models.IntegerField(null = True, blank = True, db_column='pil_crop_right')
    pil_crop_lower      = models.IntegerField(null = True, blank = True, db_column='pil_crop_lower')
    pil_crop_width      = models.IntegerField(null = True, blank = True, db_column='pil_crop_width')
    pil_crop_height     = models.IntegerField(null = True, blank = True, db_column='pil_crop_height')   
    pil_scale_x         = models.IntegerField(null = True, blank = True, db_column='pil_scale_x')
    pil_scale_y         = models.IntegerField(null = True, blank = True, db_column='pil_scale_y')
    pil_rotation        = models.IntegerField(null = True, blank = True, db_column='pil_rotation')     





def _delete_file(path):
   """ Deletes file from filesystem. """
   if os.path.isfile(path):
       os.remove(path)

@receiver(models.signals.post_delete, sender=Upload_File)
def delete_file(sender, instance, *args, **kwargs):
    """ Deletes image files on `post_delete` """
    if instance.image_file:
        _delete_file(instance.image_file.path)

@receiver(models.signals.post_delete, sender=Imagetag)
def delete_file(sender, instance, *args, **kwargs):
    """ Deletes image files on `post_delete` """
    if instance.tag:
        _delete_file(instance.tag.path)
        
@receiver(models.signals.post_delete, sender=Zipfile_Download)
def delete_file(sender, instance, *args, **kwargs):
    """ Deletes image files on `post_delete` """
    if instance.zipfile:
        _delete_file(instance.zipfile.path)
        
@receiver(models.signals.post_delete, sender=Processed_Images)
def delete_file(sender, instance, *args, **kwargs):
    """ Deletes image files on `post_delete` """
    if instance.master:
        _delete_file(instance.master.path)
    if instance.thumbnail:
        _delete_file(instance.thumbnail.path)
    if instance.thumbnail_square:        
        _delete_file(instance.thumbnail_square.path)
    if instance.medium:
        _delete_file(instance.medium.path)
    if instance.medium_square:
        _delete_file(instance.medium_square.path)
    if instance.large:
        _delete_file(instance.large.path)
    if instance.large_square:
        _delete_file(instance.large_square.path)
    if instance.social_media:
        _delete_file(instance.social_media.path)
    if instance.social_media:
        _delete_file(instance.social_media_square.path)
        

        
'''

    def delete(self):
        self.zipfile.delete()
        super(Zipfile_Download, self).delete()  

    def delete(self):
        self.image_file.delete()
        super(Upload_File, self).delete()

    def delete(self):
        self.tag.delete()
        super(Imagetag, self).delete()


    def delete(self):
        self.master.delete()
        self.thumbnail.delete()
        self.thumbnail_square.delete()
        self.medium.delete()
        self.medium_square.delete()
        self.large.delete()
        self.large_square.delete()
        self.social_media.delete()
        self.social_media_square.delete()
        super(Processed_Images, self).delete()

'''