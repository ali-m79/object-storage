
from django.contrib import admin
from django.urls import path, include
from .views import *
urlpatterns = [
    path('upload/',UploadObjectView.as_view(),name="upload" ),
    path("main/", ObjectStorageView.as_view(), name="main"),
    path('delete/<int:obj_id>/', DeleteObjectView.as_view(), name='delete'),
    path('download/<int:obj_id>/', DownloadObjectView.as_view(), name='download'),
    path('fetch-users/<int:obj_id>/', PopupView.as_view(), name='popup'),
    path('update_access_users/<int:obj_id>/', UpdateAccessUsersView.as_view(), name='update_access_users'),

]
