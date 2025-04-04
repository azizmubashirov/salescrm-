from rest_framework import generics, status
from rest_framework.views import Response
from currency.models import *
from currency.serializers import *


class CurrencyCreateApiView(generics.CreateAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializers


class CurrencyUpdateApiView(generics.UpdateAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializers
    lookup_field = 'id'
    http_method_names = ['put']
    
    def perform_update(self, serializer):
        instance = serializer.save()
        CurrencyHistory.objects.create(currency=instance, exchange_rate=instance.exchange_rate)

class CurrencyHistoryList(generics.ListAPIView):
    queryset = CurrencyHistory.objects.order_by('-timestamp')  
    serializer_class = CurrencyHistorySerializer
    
    filterset_fields = ['currency']

class CurrencyDetailView(generics.RetrieveAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializers
    lookup_field = 'id'
    
    
class CurrencyListApiView(generics.ListAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializers
    search_fields = ['name', 'symbol', 'exchange_rate']
    filterset_fields = ['is_main']


class CurrencyDeleteApiView(generics.DestroyAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencyDeleteSerializers
    
    def delete(self, request, *args, **kwargs):
        serializers = CurrencyDeleteSerializers(data=request.data)
        serializers.is_valid(raise_exception=True)

        ids = serializers.validated_data['ids']
        queryset = Currency.objects.filter(id__in=ids)
        queryset.delete()


        return Response(status=status.HTTP_204_NO_CONTENT)
