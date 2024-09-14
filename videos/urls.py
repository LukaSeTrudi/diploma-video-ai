from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("add", views.add, name="add"),
    path("upload", views.upload, name="upload"),
    path("<int:video_id>", views.video, name="video"),
    path("<int:video_id>/add_message", views.add_message, name="add_message")
]