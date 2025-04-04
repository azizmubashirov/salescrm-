from django.urls import path
from files.views import *

urlpatterns = [
    path('upload', FilesCreateApiView.as_view()),
]