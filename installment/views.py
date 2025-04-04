from django.shortcuts import render
from rest_framework import generics, status
from .models import (
    PlanMonth, 
    InstallmentPlan,
    Payment,
    Debt
    )
from .serializers import (
    MonthSerializers, 
    DeleteSerializers,
    InstallmentCreateSerializers,
    InstallmentPlanListSerializers,
    PaymentCreateSerializers, 
    PaymentListSerializers,
    InstallmentReturnSerializers,
    DebtSerializers,
    DebtUpdateSerializers,
    InstallmentPlanIdSerializers,
    InstallmentStatusSerializers,
    InstallmentCommentSerializers
)
from rest_framework.views import Response
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
import openpyxl
from django.http import HttpResponse

class MonthCreateApiView(generics.CreateAPIView):
    queryset = PlanMonth.objects.all()
    serializer_class = MonthSerializers


class MonthUpdateApiView(generics.UpdateAPIView):
    serializer_class = MonthSerializers
    queryset = PlanMonth.objects.all()
    lookup_field = 'id'
    http_method_names = ['put']

class MonthDeleteApiView(generics.DestroyAPIView):
    serializer_class = DeleteSerializers
    queryset = PlanMonth.objects.all()
    
    def delete(self, request, *args, **kwargs):
        serializers = DeleteSerializers(data=request.data)
        serializers.is_valid(raise_exception=True)

        ids = serializers.validated_data['ids']
        queryset = PlanMonth.objects.filter(id__in=ids)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class MonthDetailApiView(generics.RetrieveAPIView):
    serializer_class = MonthSerializers
    queryset = PlanMonth.objects.all()
    lookup_field = 'id'

class MonthListApiView(generics.ListAPIView):
    serializer_class = MonthSerializers
    queryset = PlanMonth.objects.all()
    permission_classes = [AllowAny]
    
    
"""Installment"""

class InstallemtFilter(django_filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = InstallmentPlan
        fields = ['client', 'client__phone_number1', 'store', 'status', 'seller', 'user', 'created_at']
        
class InstallmentCreateApiView(generics.CreateAPIView):
    queryset = InstallmentPlan.objects.all().order_by('-id')
    serializer_class = InstallmentCreateSerializers

class InstallmentUpdateApiView(generics.UpdateAPIView):
    serializer_class = InstallmentCreateSerializers
    queryset = InstallmentPlan.objects.all()
    lookup_field = 'id'
    http_method_names = ['put']
    
class InstallmentPlanApiView(generics.ListAPIView):
    serializer_class = InstallmentPlanListSerializers
    queryset = InstallmentPlan.objects.filter(status__in=(1,2, 6)).order_by('-id')
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = InstallemtFilter
    
    search_fields = ['installemt_product__product__reception__product__name', 'installemt_product__product__reception__productcode__code', 
                     'installemt_product__product__reception__ram', 'installemt_product__product__reception__memory'
                     ]

class InstallmentPlanBotApiView(generics.ListAPIView):
    serializer_class = InstallmentPlanListSerializers
    queryset = InstallmentPlan.objects.all().order_by('-id')
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = InstallemtFilter
    permission_classes = [AllowAny]
    
    search_fields = ['installemt_product__product__reception__product__name', 'installemt_product__product__reception__productcode__code', 
                     'installemt_product__product__reception__ram', 'installemt_product__product__reception__memory'
                     ]
        
class InstallmentPlanLeadApiView(generics.ListAPIView):
    serializer_class = InstallmentPlanListSerializers
    queryset = InstallmentPlan.objects.filter(status__range=(4,5)).order_by('-id')
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = InstallemtFilter
    search_fields = ['installemt_product__product__reception__product__name', 'installemt_product__product__reception__productcode__code', 
                     'installemt_product__product__reception__ram', 'installemt_product__product__reception__memory'
                     ]

class InstallmentInfoApiView(generics.RetrieveAPIView):
    serializer_class = InstallmentPlanListSerializers
    queryset = InstallmentPlan.objects.all().order_by('-id')
    lookup_field = 'id'
    permission_classes = [AllowAny]
    
class InstallmentIdApiView(generics.RetrieveAPIView):
    serializer_class = InstallmentPlanIdSerializers
    queryset = InstallmentPlan.objects.all().order_by('-id')
    lookup_field = 'id'

class InstallmentReturnApiView(generics.UpdateAPIView):
    serializer_class = InstallmentReturnSerializers
    queryset = InstallmentPlan.objects.all()
    lookup_field = 'id'
    http_method_names = ['put']
    
class InstallmentUpdateStatusApiView(generics.UpdateAPIView):
    serializer_class = InstallmentStatusSerializers
    queryset = InstallmentPlan.objects.all()
    lookup_field = 'id'
    http_method_names = ['put']

class InstallmentDeleteApiView(generics.DestroyAPIView):
    serializer_class = DeleteSerializers
    queryset = InstallmentPlan.objects.all()
    
    def delete(self, request, *args, **kwargs):
        serializers = DeleteSerializers(data=request.data)
        serializers.is_valid(raise_exception=True)

        ids = serializers.validated_data['ids']
        queryset = InstallmentPlan.objects.filter(id__in=ids)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class InstallmentUpdateCommentApiView(generics.UpdateAPIView):
    serializer_class = InstallmentCommentSerializers
    queryset = InstallmentPlan.objects.all()
    lookup_field = 'id'
    http_method_names = ['put']

class ExportPlanToExcel(generics.ListAPIView):
    queryset = InstallmentPlan.objects.filter(status__in=(1,2, 6))
    serializer_class = InstallmentPlanListSerializers
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = InstallemtFilter
    
    search_fields = ['installemt_product__product__reception__product__name', 'installemt_product__product__reception__productcode__code', 
                     'installemt_product__product__reception__ram', 'installemt_product__product__reception__memory'
                     ]

    def get(self, request, *args, **kwargs):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Рассрочка"

        headers = [
            'Клиент', 'Магазин', 'Продукт', 'Код', "Кол-во", 'Цена', 'Валюта', 'Ежемесячный платеж', 'Первый взнос', 'Месяц',  'Кассир',
            'Продавец', 'ДАТА'
        ]
        ws.append(headers)
        
        orders = self.filter_queryset(self.get_queryset())
        for order in orders:
            client_name = f"{order.client.first_name} {order.client.last_name}" if order.client else ""
            seller_name = f"{order.seller.firstname} {order.seller.lastname}" if order.seller else ""
            user_name = f"{order.user.firstname} {order.user.lastname}" if order.user else ""
            currency = order.currency.symbol if order.currency else '-'
            product_codes = ", ".join([item.code for item in order.installemt_product.all()])
            product_names = ", ".join([item.product.reception.product.name for item in order.installemt_product.all()])
            quantities =  order.installemt_product.count()
            
            ws.append([
                client_name,
                order.store.name if order.store else '',
                product_names,
                product_codes,
                quantities,
                order.total_amount,
                currency,
                f"{order.remaining_price}",
                f"{order.first_payment}",
                f"{order.month.months if order.month else ''}",
                user_name,
                seller_name,
                self.remove_tzinfo(order.created_at),
            ])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=installment_plans.xlsx'
        wb.save(response)
        return response
    
    def remove_tzinfo(self, dt):
        if dt is not None:
            return dt.replace(tzinfo=None)
        return dt

"""Payment"""
class PaymentCreateApiView(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentCreateSerializers

class DebtListApiView(generics.ListAPIView):
    queryset = Debt.objects.all()
    serializer_class = DebtSerializers
    filterset_fields = ['payment_received']
    search_fields = ['installment__client__phone_number1', 'installment__client__first_name', 'installment__client__last_name' ]

class DebtUpdateApiView(generics.UpdateAPIView):
    serializer_class = DebtUpdateSerializers
    queryset = Debt.objects.all()
    lookup_field = 'id'
    http_method_names = ['put']
    
class DebtExportApiView(generics.ListAPIView):
    serializer_class = DebtSerializers
    queryset = Debt.objects.all()
    
    def get(self, request, *args, **kwargs):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "задолжники"

        headers = [
            'Клиент', 'Сумма', 'Комментарий', "Платеж получен", 'ДАТА'
        ]
        ws.append(headers)
        
        debts = self.filter_queryset(self.get_queryset())
        for debt in debts:
            client_name = f"{debt.client.first_name} {debt.client.last_name}" if debt.client else ""
            
            ws.append([
                client_name,
                debt.outstanding_amount,
                debt.comment,
                debt.payment_received,
                self.remove_tzinfo(debt.created_at),
            ])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=debt.xlsx'
        wb.save(response)
        return response
    
    def remove_tzinfo(self, dt):
        if dt is not None:
            return dt.replace(tzinfo=None)
        return dt