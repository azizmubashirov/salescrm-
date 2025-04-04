from rest_framework import generics
from user.models import *
from user.serializers import (UserSerializers, RoleSerializers, PermissionSerializers, 
                              UserListSerializers, UserDeleteSerializers, UserUpdateSerializers)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.settings import api_settings

class UserCreateApiView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializers

class UserUpdateApiView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializers
    lookup_field = 'id'
    http_method_names = ['put']


class UserDeleteApiView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserDeleteSerializers

    def delete(self, request, *args, **kwargs):
        serializers = UserDeleteSerializers(data=request.data)
        serializers.is_valid(raise_exception=True)

        ids = serializers.validated_data['ids']
        queryset = User.objects.filter(id__in=ids)
        queryset.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

class UserDetailApiView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializers
    lookup_field = 'id'

class UserListApiView(generics.ListAPIView):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserListSerializers
    filterset_fields = ['role']
    search_fields = ['login', 'firstname', 'lastname', 'phone']

class RoleListApiView(generics.ListAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializers
    pagination_class = None
    
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "next": None,
            "previous": None,
            "page_size": 0,
            "current_page": 0,
            "total_pages": 0,
            "page_items": 0,
            "total": 0,
            "results": serializer.data
        })
    
class PermissionListApiView(generics.ListAPIView):
    queryset = Permission.objects.order_by('id')
    serializer_class = PermissionSerializers
    pagination_class = None
    
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "next": None,
            "previous": None,
            "page_size": 0,
            "current_page": 0,
            "total_pages": 0,
            "page_items": 0,
            "total": 0,
            "results": serializer.data
        })
