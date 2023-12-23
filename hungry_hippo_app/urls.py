from django.urls import path
from . import views, api

app_name = 'hungry_hippo_app'
urlpatterns = [
    # views paths
    path("", views.entry, name="entry"),
    path("register", views.register, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("index", views.index, name='index'),
    
    # API Paths
    path("upload_images_folder", api.upload_images_folder, name="upload_images_folder"),
    path("process_batch", api.process_batch, name="process_batch"),
    path('upload_tag/<int:user_image_set>', api.upload_tag, name='upload_tag'),
    path('get_browse_images/<int:user_image_set>', api.get_browse_images, name="get_browse_images"),


    # Sandbox
    # path('update_form1', sandbox.update_form1),
    # path('update_form2', sandbox.update_form2)
    # path('analyse_imageFile_Vs_PILFile/<int:user_image_set>', sandbox.analyse_imageFile_Vs_PILFile, name='analyse_imageFile_Vs_PILFile' )
    
]