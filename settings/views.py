from rest_framework import generics, status
from rest_framework.views import Response
from product.models import Settings
from .serializers import *
from rest_framework.permissions import AllowAny
from rest_framework.permissions import AllowAny


class SettingsUpdateApiView(generics.CreateAPIView):
    queryset = Settings.objects.all()
    serializer_class = SettingsUpdateSerializers
    
    
class SettingsInfoApiView(generics.RetrieveAPIView):
    serializer_class = SettingsUpdateSerializers
    permission_classes = [AllowAny]
    
    def get_object(self): 
        return Settings.objects.last()
