from rest_framework import generics, status
from rest_framework.views import Response
from store.models import *
from store.serializers import StoreSerializers, StoreListSerializers, DeleteSerializers, BalanceListSerializers
from store.models import Store
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework.views import APIView
import re
from rest_framework.permissions import AllowAny 
import openpyxl
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
import django_filters
from django.utils import timezone
from django.db.models import Sum

class StoreCreateApiView(generics.CreateAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializers

    

class StoreUpdateApiView(generics.UpdateAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializers
    lookup_field = 'id'
    http_method_names = ['put']


class StoreListApiView(generics.ListAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreListSerializers
    search_fields = ['name', 'address']
    permission_classes = [AllowAny]


class StoreDeleteApiView(generics.DestroyAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializers
    
    def delete(self, request, *args, **kwargs):
        serializers = DeleteSerializers(data=request.data)
        serializers.is_valid(raise_exception=True)

        ids = serializers.validated_data['ids']
        queryset = Store.objects.filter(id__in=ids)
        queryset.delete()


        return Response(status=status.HTTP_204_NO_CONTENT)

class StoreDetailApiView(generics.RetrieveAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreListSerializers
    lookup_field = 'id'



"""Balance"""

class BalanceFilter(django_filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = StoreBalance
        fields = ['category', 'created_at']
        
@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(name='type', description='Type of balance. Use "debit" or "credit"', type=str),
        ]
    )
)
class BalanceListApiView(generics.ListAPIView):
    queryset = StoreBalance.objects.all()
    serializer_class = BalanceListSerializers
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = BalanceFilter
    
    def get_queryset(self):
        queryset = StoreBalance.objects.all()
        balance_type = self.request.query_params.get('type')
        if balance_type == 'debit':
            queryset = queryset.exclude(debit__isnull=True)
        elif balance_type == 'credit':
            queryset = queryset.exclude(credit__isnull=True)
        return queryset
    
class BalanceApiView(APIView):
    serializer_class = BalanceListSerializers
    
    def get(self, request, *args, **kwargs):
        if kwargs['store_id']:
            balances = StoreBalance.objects.filter(store_id=kwargs['store_id'])
        else:
            balances = StoreBalance.objects.all()
        all_balance = 0
        for bal in balances:
            debit = bal.debit or 0
            credit = bal.credit or 0
            all_balance += debit - credit
        return Response({'balance': self.price_format(all_balance)}, status=status.HTTP_200_OK, content_type='application/json')
    
    def price_format(self, inp):
        price = int(inp)
        res = "{:,}".format(price)
        formated = re.sub(",", " ", res)
        return formated
    

class BalanceCreateApiView(generics.CreateAPIView):
    queryset = StoreBalance.objects.all()
    serializer_class = BalanceListSerializers

class ExportBalanceToExcel(generics.ListAPIView):
    queryset = StoreBalance.objects.all()
    serializer_class = BalanceListSerializers
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = BalanceFilter

    def remove_tzinfo(self, dt):
        if dt is not None:
            return dt.replace(tzinfo=None)
        return dt
    
    def get(self, request, *args, **kwargs):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Orders"

        headers = [
            'ОПИСАНИЕ', 'ПРИХОД', 'РАССХОД', 'ДАТА'
        ]
        ws.append(headers)

        balance = self.filter_queryset(self.get_queryset())

        for data in balance:
            ws.append([
                data.description,
                data.debit,
                data.credit,
                self.remove_tzinfo(data.created_at),
            ])
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=balance.xlsx'
        wb.save(response)
        return response
    
class ExportBalanceToExcelAdmin(generics.ListAPIView):
    queryset = StoreBalance.objects.all()
    serializer_class = BalanceListSerializers
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = BalanceFilter

    def remove_tzinfo(self, dt):
        if dt is not None:
            return dt.replace(tzinfo=None)
        return dt
    
    def get(self, request, *args, **kwargs):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Orders"

        headers = [
            'ОПИСАНИЕ', 'ПРИХОД', 'РАССХОД', 'ЧИСТОЕ РАСХОД', 'ВЫГОДА', 'ДАТА'
        ]
        ws.append(headers)

        balance = self.filter_queryset(self.get_queryset())

        for data in balance:
            ws.append([
                data.description,
                data.debit,
                data.credit,
                data.cost,
                data.profit,
                self.remove_tzinfo(data.created_at),
            ])
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=balance.xlsx'
        wb.save(response)
        return response
    
    

class DailyStoreBalanceView(APIView):
    def get(self, request, *args, **kwargs):
        today = timezone.now().date()
        store_balances_today = StoreBalance.objects.filter(created_at__date=today)
        total_debit_sum = store_balances_today.aggregate(total_debit=Sum('debit'))['total_debit'] or 0
        total_credit_sum = store_balances_today.aggregate(total_credit=Sum('credit'))['total_credit'] or 0
        total_profit_sum = store_balances_today.aggregate(total_profit=Sum('profit'))['total_profit'] or 0
        
        data = {
            "date": today,
            "total_debit": total_debit_sum,
            "total_credit": total_credit_sum,
            "total_profit": total_profit_sum
        }
        
        return Response(data)
    

class BalanceDeleteApiView(APIView):
    queryset = StoreBalance.objects.all()
    serializer_class = DeleteSerializers
    
    def delete(self, request, *args, **kwargs):
        serializers = DeleteSerializers(data=request.data)
        serializers.is_valid(raise_exception=True)

        ids = serializers.validated_data['ids']
        queryset = StoreBalance.objects.filter(id__in=ids)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)