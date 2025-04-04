from django.urls import path, include
from user.views import *

urlpatterns = [
    path('list', UserListApiView.as_view()),
    path('role-list', RoleListApiView.as_view()),
    path('permission-list', PermissionListApiView.as_view()),
    path('create', UserCreateApiView.as_view()),
    path('update/<int:id>', UserUpdateApiView.as_view()),
    path('delete', UserDeleteApiView.as_view()),
    path('info/<int:id>', UserDetailApiView.as_view()),
    
]