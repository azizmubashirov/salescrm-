from rest_framework import generics, status
from rest_framework.views import Response
from client.models import *
from client.serializers import *
from rest_framework.permissions import AllowAny

class ClientCreateApiView(generics.CreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializers
    
class ClientCreateBotApiView(generics.CreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientBotSerializers
    permission_classes = [AllowAny]


class ClientUpdateApiView(generics.UpdateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializers
    lookup_field = 'id'
    http_method_names = ['put']
    permission_classes = [AllowAny]


class ClientDeleteApiView(generics.DestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientDeleteSerializers
    
    def delete(self, request, *args, **kwargs):
        serializers = ClientDeleteSerializers(data=request.data)
        serializers.is_valid(raise_exception=True)

        ids = serializers.validated_data['ids']
        queryset = Client.objects.filter(id__in=ids)
        queryset.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ClientListApiView(generics.ListAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientListSerializers
    filterset_fields = ['status', 'phone_number1']
    search_fields = ['first_name', 'last_name', 'phone_number1', 'phone_number2', 'tab_number']
    permission_classes = [AllowAny]


class ClientDetailApiView(generics.RetrieveAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientListSerializers
    lookup_field = 'id'

class ClientInfoForBotDetailApiView(generics.RetrieveAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientListSerializers
    lookup_field = 'chat_id'
    permission_classes = [AllowAny]


"""Discount Level """
class DiscountLevelCreateApiView(generics.CreateAPIView):
    queryset = DiscountLevel.objects.all()
    serializer_class = DiscountLevelSerializers
    
class DiscountLevelUpdateApiView(generics.UpdateAPIView):
    queryset = DiscountLevel.objects.all()
    serializer_class = DiscountLevelSerializers
    lookup_field = 'id'
    http_method_names = ['put']
    
class DiscountLevelDeleteApiView(generics.DestroyAPIView):
    queryset = DiscountLevel.objects.all()
    serializer_class = ClientDeleteSerializers
    
    def delete(self, request, *args, **kwargs):
        serializers = ClientDeleteSerializers(data=request.data)
        serializers.is_valid(raise_exception=True)

        ids = serializers.validated_data['ids']
        queryset = DiscountLevel.objects.filter(id__in=ids)
        queryset.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

class DiscountLevelListApiView(generics.ListAPIView):
    queryset = DiscountLevel.objects.all()
    serializer_class = DiscountLevelSerializers
    
class DiscountLevelDetailApiView(generics.RetrieveAPIView):
    queryset = DiscountLevel.objects.all()
    serializer_class = DiscountLevelSerializers
    lookup_field = 'id'
    
"""Discount Client"""
class ClientLevelListApiView(generics.ListAPIView):
    queryset = Discount.objects.all()
    serializer_class = CLientLevelSerializers
    
class ClientLevelUpdateApiView(generics.UpdateAPIView):
    queryset = Discount.objects.all()
    serializer_class = CLientLevelUpdateSerializers
    lookup_field = 'id'
    http_method_names = ['put']
    
class ClientLevelCreateApiView(generics.CreateAPIView):
    queryset = Discount.objects.all()
    serializer_class = ClientlevelCreateSerializers
    