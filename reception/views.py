from rest_framework import generics
from reception.models import *
from store.models import PriceList
from product.models import ActiveProduct
from reception.serializers import (ReceptionSerializers, ReceptionCreateSerializers,
                                   ReceptionUpdateSerializers, PriceListSerializers,
                                   PriceSerializers, StoreProductSerializers,
                                   SwopeHistorySerializers, SwopeHistoryListSerializers,
                                    ReceptionDetailSerializers,
                                   CreateBarCodeSerializers, StoreProductEditSerializers, 
                                   ReceptionPhoneNumberSerializer, DeleteSerializers, 
                                   ReceptionUpdateStatusSerializers, ReceptionReturnSerializers,
                                   StoreProductWebSerializers, ReceptionSerializers2, CodeSerializers)
from product.serializers import *
from currency.serializers import *
from reception.models import Reception
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db.models import Sum
from django.http import HttpResponse
import openpyxl
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from django.utils import timezone
from django.db.models import Max, DecimalField
from django.db.models.functions import Coalesce
from django_filters import rest_framework as filters
from .filters import StoreProductFilter
from django.db.models import OuterRef, Subquery, Max, F, Q
from django.db.models.functions import Coalesce
from django.db.models.functions import RowNumber
from django.db import connection

class ReceptionCreateApiView(generics.CreateAPIView):
    queryset = Reception.objects.all()
    serializer_class = ReceptionCreateSerializers
    

class ReceptionUpdateApiView(generics.UpdateAPIView):
    queryset = Reception.objects.all()
    serializer_class = ReceptionUpdateStatusSerializers
    lookup_field = 'id'
    http_method_names = ['put']


class ReceptionFilter(django_filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Reception
        fields = ['type', 'region', 'color', 'box', 'store', 'status', 'created_at', 'product__brand', 'product', 'user']
        
        
class ReceptionListApiView(generics.ListAPIView):
    queryset = Reception.objects.all()
    serializer_class = ReceptionSerializers2
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ReceptionFilter
    search_fields = ['product__name', 'productcode__code', 'ram', 'memory', 'full_name', 'phone_number']

class ReceptionReturnApiView(generics.UpdateAPIView):
    queryset = Reception.objects.all()
    serializer_class = ReceptionReturnSerializers
    lookup_field = 'id'
    http_method_names = ['put']

class ReceptionEditApiView(generics.UpdateAPIView):
    queryset = Reception.objects.all()
    serializer_class = ReceptionUpdateSerializers
    lookup_field = 'id'
    http_method_names = ['put']
    
class SellerListApiView(generics.ListAPIView):
    queryset = Reception.objects.values('phone_number', 'full_name').annotate(
            total_count=Sum('count')
    )
    serializer_class = ReceptionPhoneNumberSerializer
    pagination_class = None

class ExportReceptionToExcel(generics.ListAPIView):
    queryset = Reception.objects.all()
    serializer_class = ReceptionSerializers
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ReceptionFilter
    search_fields = ['product__name', 'productcode__code', 'ram', 'memory', 'full_name', 'phone_number']

    def get(self, request, *args, **kwargs):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Receptions"

        headers = [
            'Продукт', 'Код', 'Сотрудник', 'Тип', 'Коробка',
            'Цена', 'Валюта', 'Поставщик', 'Номер телефона', 'Магазин',
            'Статус оплаты', 'Комментарий', 'Дата и время'
        ]
        ws.append(headers)

        receptions = self.filter_queryset(self.get_queryset())
        for reception in receptions:
            for item in reception.productcode_set.filter(reception=reception, store=reception.store):
                ws.append([
                f"{reception.product.name} {reception.region.name} {reception.color.name_ru} {reception.ram}/{reception.memory}",  
                    item.code,
                    reception.user.login if reception.user else "--",
                    reception.type.name,
                    "есть" if reception.box else 'нет',
                    f"{reception.price}",
                    f"{reception.currency.symbol}",
                    reception.full_name,
                    reception.phone_number,
                    reception.store.name,
                    reception.get_status_display(),
                    reception.comment,
                    self.remove_tzinfo(reception.created_at),
                ])
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=reception.xlsx'
        wb.save(response)
        return response
    
    def remove_tzinfo(self, dt):
        if dt is not None:
            return dt.replace(tzinfo=None)
        return dt

class ReceptionDetailApiView(generics.RetrieveAPIView):
    queryset = Reception.objects.all()
    serializer_class = ReceptionDetailSerializers
    lookup_field = 'id'
    
class ReceptionDeleteApiView(APIView):
    queryset = Reception.objects.all()
    serializer_class = DeleteSerializers
    
    def delete(self, request, *args, **kwargs):
        serializers = DeleteSerializers(data=request.data)
        serializers.is_valid(raise_exception=True)

        ids = serializers.validated_data['ids']
        queryset = Reception.objects.filter(id__in=ids)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

"""Price"""
class PriceListApiView(generics.ListAPIView):
    queryset = PriceList.objects.all()
    serializer_class = PriceListSerializers
    filterset_fields = ['store']
    search_fields = ['product__name']

class PriceDetailApiView(generics.RetrieveAPIView):
    queryset = PriceList.objects.all()
    serializer_class = PriceSerializers
    lookup_field = 'id'
    
class PriceUpdateApiView(generics.UpdateAPIView):
    queryset = PriceList.objects.all()
    serializer_class = PriceSerializers
    lookup_field = 'id'
    http_method_names = ['put']
    
    
class PriceCreateApiView(generics.CreateAPIView):
    queryset = PriceList.objects.all()
    serializer_class = PriceSerializers

class PriceListDeleteApiView(APIView):
    queryset = PriceList.objects.all()
    serializer_class = DeleteSerializers
    
    def delete(self, request, *args, **kwargs):
        serializers = DeleteSerializers(data=request.data)
        serializers.is_valid(raise_exception=True)

        ids = serializers.validated_data['ids']
        queryset = PriceList.objects.filter(id__in=ids)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
"""Store Product"""
class ProductFilter(django_filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter()
    price = django_filters.RangeFilter()
    reception__type = django_filters.BaseInFilter(field_name='reception__type', lookup_expr='in')
    reception__region = django_filters.BaseInFilter(field_name='reception__region', lookup_expr='in')
    reception__color = django_filters.BaseInFilter(field_name='reception__color', lookup_expr='in')
    reception__box = django_filters.BaseInFilter(field_name='reception__box', lookup_expr='in')
    reception__product__brand = django_filters.BaseInFilter(field_name='reception__product__brand', lookup_expr='in')
    reception__ram = django_filters.BaseInFilter(field_name='reception__ram', lookup_expr='in')
    reception__memory = django_filters.BaseInFilter(field_name='reception__memory', lookup_expr='in')
    reception__product__category__parent__slug = django_filters.CharFilter(method='filter_by_category')
    class Meta:
        model = StoreProduct
        fields = ['reception__type', 'reception__region', 'reception__color', 'reception__box', 'reception__product__brand', 'store', 'reception__product', 
                  'reception__product__is_popular', 'price', 'reception__ram', 'reception__memory', 'reception__product__category__parent__slug']
    
    def filter_by_category(self, queryset, name, value):
        return queryset.filter(
            Q(reception__product__category__parent__slug=value) |
            Q(reception__product__category__slug=value)
        )
        
class StoreProductListApiView(generics.ListAPIView):
    queryset = StoreProduct.objects.filter(sell=False)
    serializer_class = StoreProductSerializers
    filterset_fields = ['reception__type', 'reception__region', 'reception__color', 'reception__box', 'reception__product__brand', 'store', 'reception__product']
    search_fields = ['reception__product__name', 'reception__productcode__code', 'reception__ram', 'reception__memory']
        
class StoreProductWebListAPiView(generics.ListAPIView):
    serializer_class = StoreProductSerializers
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['reception__product__name', 'reception__productcode__code', 'reception__ram', 'reception__memory']
    
    def get_queryset(self):
        subquery = StoreProduct.objects.filter(
            reception__product=OuterRef('reception__product'),
            reception__color=OuterRef('reception__color'),
            reception__region=OuterRef('reception__region'),
            reception__ram=OuterRef('reception__ram'),
            reception__memory=OuterRef('reception__memory'),
            reception__type=OuterRef('reception__type'),
            reception__product__brand=OuterRef('reception__product__brand'),
            reception__currency=OuterRef('reception__currency')
        ).annotate(
            max_price=Max('price')
        ).values(
            'reception__product',
            'reception__color',
            'reception__region',
            'reception__ram',
            'reception__memory',
            'reception__type',
            'reception__product__brand',
            'reception__currency'
        ).order_by('-max_price')[:1]

        active_products = ActiveProduct.objects.filter(status=True).values_list('product_id', flat=True)

        annotated_queryset = StoreProduct.objects.filter(
            id__in=Subquery(subquery.values('id'))
        ).filter(reception__product_id__in=active_products)
        
        return annotated_queryset

class ProductFilter(django_filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = StoreProduct
        fields = ['reception__type', 'reception__region', 'reception__color', 'reception__box', 'reception__product__brand', 'store']
        
class ExportProductToExcel(generics.ListAPIView):
    queryset = StoreProduct.objects.filter(sell=False)
    serializer_class = StoreProductSerializers
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['reception__product__name', 'reception__productcode__code', 'reception__ram', 'reception__memory']

    def get(self, request, *args, **kwargs):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Products"

        headers = [
            'Продукт', 'Цвет', 'Модель', 'Код', 'Магазин', 'Цена', 'Дата и время'
        ]
        ws.append(headers)

        products = self.filter_queryset(self.get_queryset())

        for product in products:
            codes = ProductCode.objects.filter(reception=product.reception, store=product.store)
            for item in codes:
                code_str = item.code

                ws.append([
                    product.reception.product.name,
                    product.reception.color.name_ru,
                    product.reception.product.brand.name,
                    code_str,
                    product.store.name,
                    product.price,
                    self.remove_tzinfo(product.created_at),
                ])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=product.xlsx'
        wb.save(response)
        return response
    
    def remove_tzinfo(self, dt):
        if dt is not None:
            return dt.replace(tzinfo=None)
        return dt
    
class StoreProductBotListApiView(generics.ListAPIView):
    queryset = StoreProduct.objects.filter(sell=False)
    serializer_class = StoreProductSerializers
    filterset_fields = ['reception__type', 'reception__region', 'reception__color', 'reception__box', 'reception__product__brand', 'store', 'reception__ram', 'reception__memory', 'reception__product__category']
    search_fields = ['reception__product__name', 'reception__productcode__code']
    permission_classes = [AllowAny]
    
class StoreProductDetailApiView(generics.RetrieveAPIView):
    queryset = StoreProduct.objects.filter(sell=False)
    serializer_class = StoreProductSerializers
    lookup_field = 'id'
    permission_classes = [AllowAny]
    
class StoreProductDetailSlugApiView(generics.RetrieveAPIView):
    queryset = StoreProduct.objects.filter()
    serializer_class = StoreProductSerializers
    lookup_field = 'slug'
    permission_classes = [AllowAny]
    
class StoreProductBotDetailApiView(generics.RetrieveAPIView):
    queryset = StoreProduct.objects.filter(sell=False)
    serializer_class = StoreProductSerializers
    lookup_field = 'id'
    permission_classes = [AllowAny]

class StoreProductEditApiView(generics.UpdateAPIView):
    queryset = StoreProduct.objects.filter(sell=False)
    serializer_class = StoreProductEditSerializers
    lookup_field = 'id'
    http_method_names = ['put']
    
"""SwopeCreate"""
class SwopeCreateApiView(generics.CreateAPIView):
    queryset = SwopeHistory.objects.all()
    serializer_class = SwopeHistorySerializers
    
    
class SwopeListApiView(generics.ListAPIView):
    queryset = SwopeHistory.objects.all()
    serializer_class = SwopeHistoryListSerializers
    
    def get_queryset(self):
        to_store_id = self.kwargs['to_store']
        return SwopeHistory.objects.filter(to_store_id=to_store_id)
    
class SwopeListAllApiView(generics.ListAPIView):
    queryset = SwopeHistory.objects.all()
    serializer_class = SwopeHistoryListSerializers

class SwopeDetailApiView(generics.RetrieveAPIView):
    queryset = SwopeHistory.objects.all()
    serializer_class = SwopeHistoryListSerializers
    lookup_field = 'id'
    
"""Barcode"""
class BarCodeCreateApiView(APIView):
    serializer_class = CreateBarCodeSerializers
    
    def post(self, request, *args, **kwargs):
        serializer = CreateBarCodeSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_200_OK)
    
    
class DailySalesView(APIView):
    def get(self, request, *args, **kwargs):
        today = timezone.now().date()
        orders_today = Reception.objects.filter(created_at__date=today)
        
        total_price = orders_today.aggregate(total=Sum('total_price'))['total'] or 0
        total_orders = orders_today.count()
        
        data = {
            "date": today,
            "total_orders": total_orders,
            "total_price": total_price
        }
        return Response(data)
    
class StoreProductSummaryView(APIView):
    def get(self, request, *args, **kwargs):
        total_quantity = StoreProduct.objects.filter(sell=False).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        products = StoreProduct.objects.filter(sell=False)
        total_price = 0
        for product in products:
            total_price += product.quantity * product.price      
        data = {
            "total_quantity": total_quantity,
            "total_sum_prices": total_price
        }
        
        return Response(data)
    

class CodeApiView(generics.ListAPIView):
    serializer_class = CodeSerializers

    def get_queryset(self):
        reception_id = self.kwargs['reception_id']
        store_id = self.kwargs['store_id']
        return ProductCode.objects.filter(reception_id=reception_id, store_id=store_id, sell=False)
    