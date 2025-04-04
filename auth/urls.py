from django.urls import path, include
from .views import *

urlpatterns = [
    path('login', UserLoginView.as_view()),
    path('refresh', TokenRefreshView.as_view()),
    path('logout', LogoutView.as_view()),
    
]