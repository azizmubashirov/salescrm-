from .models import Order, Type
from client.models import Client
from rest_framework import generics
from rest_framework.views import APIView
from .serializers import OrderListSerializers, OrderCreateSerializers, AmoCrmOrderSerializers, OrderInfoSerializers, OrderStatusSerializers, OrderReturnSerializers, OrderCommentSerializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import requests
import math
from decimal import Decimal
import openpyxl
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
import django_filters
from django.utils import timezone
from django.db.models import Sum
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from installment.models import InstallmentPlan
from installment.serializers import DeleteSerializers

class OrderCreateApiView(generics.CreateAPIView):
    queryset = Order.objects.all().order_by('-id')
    serializer_class = OrderCreateSerializers
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        a = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({'file': f"media/invoice/modified_invoice.png"}, status=status.HTTP_201_CREATED, headers=headers)

class OrderFilter(django_filters.FilterSet):
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Order
        fields = ['orderitem__product__reception__type', 'orderitem__product__reception__region',
                'orderitem__product__reception__color', 'orderitem__product__reception__box', 'store',
                'price_type', 'currency', 'delivery', 'status', 'client', 'created_at', 'delivery_user', 'seller', 'user']

class OrderListApiView(generics.ListAPIView):
    queryset = Order.objects.filter(status__in=(1,2,3,6))
    serializer_class = OrderListSerializers
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = OrderFilter
    
    search_fields = ['orderitem__product__reception__product__name', 'orderitem__product__reception__productcode__code', 
                     'orderitem__product__reception__ram', 'orderitem__product__reception__memory'
                     ]
    
class OrderLeadApiView(generics.ListAPIView):
    queryset = Order.objects.filter(status__range=(4, 5))
    serializer_class = OrderListSerializers
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = OrderFilter
    
    search_fields = ['orderitem__product__reception__product__name', 'orderitem__product__reception__productcode__code', 
                     'orderitem__product__reception__ram', 'orderitem__product__reception__memory'
                     ]

class OrdersForBotListApiView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderListSerializers
    permission_classes = [AllowAny]
    filterset_fields = ['client__chat_id', 'client__phone_number1']

class OrderDetailApiView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderInfoSerializers
    lookup_field = 'id'

class OrderUpdateApiView(generics.UpdateAPIView):
    serializer_class = OrderCreateSerializers
    queryset = Order.objects.all()
    lookup_field = 'id'
    http_method_names = ['put']
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'file': 'media/invoice/modified_invoice.png'}, status=status.HTTP_201_CREATED)
 
class AmoCrmOrder(generics.GenericAPIView):
    serializer_class = AmoCrmOrderSerializers
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        response = self.send_leads(data)
        client = Client.objects.filter(phone_number1=data['phone_number']).first()
        if not client:
            client = Client.objects.create(first_name=data['first_name'], last_name=data['last_name'], phone_number1=data['phone_number'])
        if data['type'] == 1:
            Order.objects.create(client=client, comment=f"{data['name']} доставка:{data['delivery']}", status=4)
        else:
            InstallmentPlan.objects.create(
                client=client,
                comment=f"{data['name']} месяц:{data['month']} доставка:{data['delivery']}",
                status = 4
            )
        return Response(response, status=status.HTTP_201_CREATED)
    
    def send_leads(self, data):
        url = "https://applebrouz.amocrm.ru/api/v4/leads/complex"
        headers = {'Authorization': f"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjVlYjExMjU1NDVjOTUwNjVhZDQzMDIyZmIwMDUzNmQxMTZiN2I2ZmIxNDA2YzQ2ZTUyYWNhMGZjY2MwYjIwYjBiNmNmY2Y5YjZhZTBkNjEzIn0.eyJhdWQiOiI5YmZiZWFmZi03OWM2LTQ5MGUtODQ3YS01OGI4NzczYzlhMDgiLCJqdGkiOiI1ZWIxMTI1NTQ1Yzk1MDY1YWQ0MzAyMmZiMDA1MzZkMTE2YjdiNmZiMTQwNmM0NmU1MmFjYTBmY2NjMGIyMGIwYjZjZmNmOWI2YWUwZDYxMyIsImlhdCI6MTcxNjU2NzExMSwibmJmIjoxNzE2NTY3MTExLCJleHAiOjE3OTg3NjE2MDAsInN1YiI6IjExMDM4Njc4IiwiZ3JhbnRfdHlwZSI6IiIsImFjY291bnRfaWQiOjMxNzI2Nzk0LCJiYXNlX2RvbWFpbiI6ImFtb2NybS5ydSIsInZlcnNpb24iOjIsInNjb3BlcyI6WyJjcm0iLCJmaWxlcyIsImZpbGVzX2RlbGV0ZSIsIm5vdGlmaWNhdGlvbnMiLCJwdXNoX25vdGlmaWNhdGlvbnMiXSwiaGFzaF91dWlkIjoiNjM2ZjExY2UtODNjYi00MGM3LTliZDMtZDdlZDQ0YjRkZDEyIn0.G5v5SsUYX3UOMFxEbK5pSdNDohfrSKE9UNaClga6kztoCLkemmmau0aqPhKfliXT7Gb6F-bDlAwsuxiwS-oWJVAEoYPMnvugeUfcsPnlyE27C7FOZYmKKgHdTPkd5elicm8uWo_XSbqvRxkKtir0YFX936E31ALEQK0tESuM_QllwLiiYpMVlsdRTtv6sibqexj_kx-1Hu_HrZHvqlmjVB_MlTdHKwhaMPWJb_Y0zvji2xanW7YoCXTZ6UVItPP4MQ_CovVdHkxlwJ9z71BXuaYm97rm7dYxpxaULIOygO_XE-TLFJ6daiCUlQ9x3_EcX3d7Xvdb_YMM_tyf-tEl9g"}
        price = data.get('price', 0)
        price = math.ceil(int(Decimal(price)))
        poyload = [
            {
                "name": f"{data['name']}",
                "price": price,
                "status_id": 66421130,
                "custom_fields_values": [
                    {
                        "field_id": 411609,
                        "values": [
                            {
                                    "value": f"{data['name']}"
                            }
                        ]
                    },
                    {
                        "field_id": 411625,
                        "values": [
                            {
                                "value": f"{data['month']}"
                            } if data['type'] == 2 else {}
                        ]
                    },
                    {
                        "field_id": 411621,
                        "values": [
                            {
                                 "value": "Наличные" if data['type'] == 1 else "Рассрочка"
                            }
                        ]
                    },
                    {
                        "field_id": 411611,
                        "values": [
                            {
                                 "value": data['delivery']
                            }
                        ]
                    }
                    
                ],
                "_embedded":{
                    "contacts":[
                        {
                        "first_name":f"{data['first_name']} {data['last_name']}",
                        "custom_fields_values":[
                            {
                                "field_code":"PHONE",
                                "values":[
                                    {
                                    "enum_code":"WORK",
                                     "value":f"{data['phone_number']}"
                                    }
                                ]
                            }
                        ]
                        }
                    ]
                }
            }
        ]
        try:
            response = requests.post(url=url, json=poyload, headers=headers)
            response.raise_for_status()
            return {'status': 200, 'message': 'Информация успешно добавлена'}
        except requests.exceptions.RequestException as e:
            return {'status': 400, 'message': "Произошла ошибка при добавлении информации"}
        
class OrderStatusEditApiView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderStatusSerializers
    lookup_field = 'id'
    http_method_names = ['put']

class OrderReturnApiView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderReturnSerializers
    lookup_field = 'id'
    http_method_names = ['put']
    
class OrderDeleteApiView(generics.DestroyAPIView):
    serializer_class = DeleteSerializers
    queryset = Order.objects.all()
    
    def delete(self, request, *args, **kwargs):
        serializers = DeleteSerializers(data=request.data)
        serializers.is_valid(raise_exception=True)

        ids = serializers.validated_data['ids']
        queryset = Order.objects.filter(id__in=ids)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OrderCommentApiView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderCommentSerializers
    lookup_field = 'id'
    http_method_names = ['put']

class ExportOrderToExcel(generics.ListAPIView):
    queryset = Order.objects.filter(status__in=(1,2,3,6))
    serializer_class = OrderListSerializers
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = OrderFilter
    
    search_fields = ['orderitem__product__reception__product__name', 'orderitem__product__reception__productcode__code', 
                     'orderitem__product__reception__ram', 'orderitem__product__reception__memory'
                     ]

    def get(self, request, *args, **kwargs):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Orders"

        headers = [
            'Клиент', 'Код', "продукт", 'Цена', 'Скидка', 'процент', 'Итоговая цена', 'Кешбек', 'Валюта', 'Кассир', 'Доставка',
            'Продавец', 'Comment', 'ДАТА'
        ]
        ws.append(headers)

        orders = self.filter_queryset(self.get_queryset())

        for order in orders:
            for item in order.orderitem_set.all():
                user_name = f"{order.user.firstname} {order.user.lastname}" if order.user else ""
                delivery_user_name = f"{order.delivery_user.firstname} {order.delivery_user.lastname}" if order.delivery_user else ""
                seller_name = f"{order.seller.firstname} {order.seller.lastname}" if order.seller else ""
                currency = order.currency.symbol if order.currency else '-'
                ws.append([
                    f"{order.client.first_name} {order.client.last_name}",
                    item.code,
                    f"{item.product}",
                    f"{item.price}",
                    f"{order.discount_amount / order.orderitem_set.count()}",
                    f"{order.discount_percentage} %",
                    self.calculate_price(order, item),
                    order.cashback_price / order.orderitem_set.count(),
                    currency,
                    user_name,
                    delivery_user_name,
                    seller_name,
                    order.comment,
                    self.remove_tzinfo(order.created_at),
                ])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=orders.xlsx'
        wb.save(response)
        return response
    
    def remove_tzinfo(self, dt):
        if dt is not None:
            return dt.replace(tzinfo=None)
        return dt

    def calculate_price(self, instance, item):
        price = item.price if item.price is not None else 0
        discount_percentage = instance.discount_percentage if instance.discount_percentage is not None else 0
        discount_amount = instance.discount_amount / instance.orderitem_set.count() if instance.discount_amount is not None else 0
        if discount_percentage and discount_amount:
            price -= (price * discount_percentage / 100) + discount_amount
        elif discount_percentage:
            price -= (price * discount_percentage) / 100
        elif discount_amount:
            price -= discount_amount

        return price if price else 0
    
class DailySalesView(APIView):
    def get(self, request, *args, **kwargs):
        today = timezone.now().date()
        orders_today = Order.objects.filter(created_at__date=today, status__range=(1, 3))
        total_price = orders_today.aggregate(total=Sum('price'))['total'] or 0
        total_orders = orders_today.count()
        data = {
            "date": today,
            "total_orders": total_orders,
            "total_price": total_price
        }
        return Response(data)
    
class GenerateOrderImageView(APIView):

    def generate_order_image(self, order, price):
        image = Image.open('invoice.png')
        font_title = ImageFont.truetype("Roboto-Medium.ttf", 35)
        font = ImageFont.truetype("Roboto-Medium.ttf", 30)
        font_pro = ImageFont.truetype("Roboto-Medium.ttf", 25)
        font_color = (0, 0, 0)

        draw = ImageDraw.Draw(image)
        price_type_display = dict(Type.choices).get(order.price_type)
        
        y_position = 200
        draw.text((50, y_position), f"Заказ: {order.id}", font=font_title, fill='black')
        y_position += 40
        
        text_lines = [
            f"Данные клиента: {order.client.first_name} {order.client.last_name}",
            f"Номер телефона: {order.client.phone_number1}",
            f"Цена (сумм): {self.price_format(round(price))} сум",
            f"Тип оплаты: {price_type_display}",
            f"Магазин: {order.store.name}",
            f"Продавец: {order.seller.firstname}",
            f"Кассир: {order.user.firstname}",
            f"Дата: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
        ]
        y_position = 250
        for line in text_lines:
            draw.text((50, y_position), line, font=font, fill=font_color)
            y_position += 50

        y_position += 20
        draw.text((50, y_position), "Продукты:", font=font_title, fill='black')
        y_position += 50
        a = 1
        for item in order.orderitem_set.all():
            product_details = f"{a}. {item.product.reception.product.name} {item.product.reception.region.name} - Код: {item.code}"
            a += 1
            draw.text((50, y_position), product_details, font=font_pro, fill='black')
            y_position += 30
            
        return image

    def get(self, request, order_id, *args, **kwargs):
        try:
            order = Order.objects.get(id=order_id)
            price = self.calculate_price(order)
            image = self.generate_order_image(order, price * order.currency.exchange_rate)

            image.save(settings.MEDIA_ROOT+"invoice/modified_invoice.png")            
            return Response({'file': 'media/invoice/modified_invoice.png'}, status=status.HTTP_201_CREATED)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    def calculate_price(self, order):
        if order.discount_percentage and order.discount_amount:
            price = order.price - (order.price * order.discount_percentage / 100) - order.discount_amount
        elif order.discount_percentage:
            price = order.price - ((order.price * order.discount_percentage) / 100)
        elif order.discount_amount:
            price = order.price - order.discount_amount
        else:
            price = order.price
        return price or 0

    def price_format(self, price):
        return "{:,}".format(price).replace(',', ' ')