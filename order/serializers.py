from rest_framework import serializers
from .models import Order, Type, OrderItem, ReturnOrderHistory
from client.serializers import ClientSerializers
from reception.serializers import StoreProductSerializers
from currency.serializers import CurrencySerializers
from user.serializers import UserListSerializers
from store.serializers import StoreListSerializers

from reception.models import StoreProduct, ProductCode
from store.models import StoreBalance
from client.models import Client, DiscountLevel, Discount, Cashback
from product.models import Settings
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
import os
from dotenv import load_dotenv
import asyncio
from decimal import Decimal
from django.db import transaction
import re
import math
import telebot

load_dotenv()

class OrderItemListSerializers(serializers.ModelSerializer):
    product = StoreProductSerializers()
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'code', 'price')

class OrderItemCreateSerializers(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'code', 'price')
        
class OrderListSerializers(serializers.ModelSerializer):
    client = ClientSerializers()
    currency = CurrencySerializers()
    user = UserListSerializers()
    delivery_user = UserListSerializers()
    seller = UserListSerializers()
    store = StoreListSerializers()
    sum_price = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    products = OrderItemListSerializers(many=True, source='orderitem_set')
    
    class Meta:
        model = Order
        fields = ('id', 'client', 'price', 'discount_amount', 'discount_percentage', 'price_type', 'currency', 'user', 'delivery', 
                  'delivery_user', 'store', 'status', 'comment', "seller", 'created_at', 'updated_at', 'sum_price', 'total_price', 'products', 'cashback_price')

    def get_sum_price(self, obj: Order):
        if obj.currency:
            return obj.price * obj.currency.exchange_rate
        else:
            return obj.price
    
    def get_total_price(self, obj:Order):
        if obj.discount_percentage and obj.discount_amount:
            price = obj.price - (obj.price * obj.discount_percentage / 100) - obj.discount_amount
        elif obj.discount_percentage:
            price = obj.price - (obj.price * obj.discount_percentage) / 100
        elif obj.discount_amount:
            price = obj.price - obj.discount_amount
        else:
            price = obj.price
        return price if price else 0

class OrderInfoSerializers(serializers.ModelSerializer):
    products = OrderItemListSerializers(many=True, source='orderitem_set')
    store = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ('id', 'client', 'price', 'discount_amount', 'discount_percentage', 'price_type', 'currency', 'user', 'delivery', 
                  'delivery_user', 'store', 'status', 'comment', "seller", "products", 'created_at', 'updated_at', 'cashback_price')

    def get_store(self, obj):
        request = self.context.get('request')
        if request and hasattr(request.user, 'store'):
            return request.user.store_id
        return None
    
class OrderStatusSerializers(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'status', 'seller')
    
    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.seller = validated_data.get('seller', instance.seller)
        
        price = self.calculate_price(instance)
        self.record_store_balance(instance, price)
        self.update_client_cashback(instance, price)
        self.apply_discounts_for_client(instance)
        return super().update(instance, validated_data)
    
    def calculate_price(self, instance):
        if instance.status == 2 or instance.status == 3:
            if instance.discount_percentage and instance.discount_amount:
                price = instance.price - (instance.price * instance.discount_percentage / 100) - instance.discount_amount
            elif instance.discount_percentage:
                price = instance.price - ((instance.price * instance.discount_percentage) / 100)
            elif instance.discount_amount:
                price = instance.price - instance.discount_amount
            else:
                price = instance.price
            return math.ceil(price)
        return 0
    
    def record_store_balance(self, instance, price):
        order_item = instance.orderitem_set.all()
        codes = [products.code for products in order_item]
        s_price = 0
        cost = 0
        for product in order_item:
            s_price += product.product.reception.price
            cost += product.product.reception.price
        s_price = price - s_price
        if instance.status == 3:
            StoreBalance.objects.create(
                debit=price,
                profit=s_price,
                cost=cost,
                description=f"Продажа {'-'.join(codes)}",
                store=instance.store,
                category=1
            )
    
    def update_client_cashback(self, instance, price):
        if instance.status == 3:
            setting = Settings.objects.last()
            client_cash = Cashback.objects.filter(client=instance.client).first()
            if client_cash:
                if instance.discount_amount and client_cash.amount >= instance.discount_amount:
                    client_cash.amount -= instance.discount_amount
                elif instance.discount_amount and client_cash.amount <= instance.discount_amount:
                    client_cash.amount = 0
                client_cash.amount += price * Decimal(setting.product_discount) / 100
                client_cash.save()
            else:
                Cashback.objects.create(client=instance.client, amount=price * Decimal(setting.product_discount) / 100)
            instance.cashback_price = Decimal(price) * Decimal(setting.product_discount) / 100
            instance.save()
    
    def apply_discounts_for_client(self, instance):
        if instance.status == 3:
            discounts = DiscountLevel.objects.all().order_by('-id')
            
            for discount_data in discounts:
                end_date = timezone.now()
                start_date = end_date - timedelta(days=int(discount_data.month) * 31)
                
                orders_price = Order.objects.filter(
                    client=instance.client,
                    created_at__range=(start_date, end_date)
                ).aggregate(total_price=Sum('price'))['total_price'] or 0
                if orders_price >= discount_data.limit:
                    discount_client = Discount.objects.filter(client=instance.client).first()
                    
                    if discount_client:
                        discount_client.level = discount_data
                        discount_client.status = False
                        discount_client.save()
                        break
                    else:
                        Discount.objects.create(
                            level=discount_data,
                            client=instance.client,
                            status=False
                        )
                        break
    
class OrderReturnSerializers(serializers.ModelSerializer):
    item_ids = serializers.ListSerializer(child=serializers.IntegerField(), write_only=True, required=True)
    class Meta:
            model = Order
            fields = ('item_ids', 'status')

    def update(self, instance, validated_data):
        try:
            item_ids = validated_data.pop('item_ids', [])
            price = self.calculate_price(instance, item_ids)
            self.record_store_balance(instance, price, item_ids)
            self.update_product_and_code(instance, item_ids)
            self.update_client_cashback(instance, item_ids)
            self.create_history_order_return(instance, item_ids)
            
            instance.status = validated_data.get('status', instance.status)
            # instance.comment = validated_data.get('comment', instance.comment)
            return super().update(instance, validated_data)
        except Exception as e:
            raise serializers.ValidationError({"non_field_errors": [f"Произошла ошибка при сохранении: {e}"]})
    
    def calculate_price(self, instance, item_ids):
        price = 0.0
        for item in instance.orderitem_set.all():
            if item.id in item_ids:
                if instance.discount_percentage and instance.discount_amount:
                    price += float(item.price) - (float(item.price) * float(instance.discount_percentage) / 100) - (float(instance.discount_amount) / instance.orderitem_set.count())
                elif instance.discount_percentage:
                    price += float(item.price) - ((float(item.price) * float(instance.discount_percentage)) / 100)
                elif instance.discount_amount:
                    price += float(item.price) - (float(instance.discount_amount) / float(instance.orderitem_set.count()))
                else:
                    price += float(item.price)
        return price
    
    def update_client_cashback(self, instance, item_ids):
        discount_amount = instance.discount_amount / instance.orderitem_set.count() * item_ids.__len__()
        client_cash = Cashback.objects.filter(client=instance.client).first()
        if client_cash:
            if instance.discount_amount and client_cash.amount >= discount_amount:
                client_cash.amount -= discount_amount
            elif instance.discount_amount and client_cash.amount <= discount_amount:
                client_cash.amount = 0
            client_cash.save()
     
    def record_store_balance(self, instance, price, item_ids):
        if instance.status in (2,3):
            codes = [products.code for products in instance.orderitem_set.all() if products.id in item_ids]
            StoreBalance.objects.create(
                    credit=price,
                    description=f"Возврат Продажа {'-'.join(codes)}",
                    store=instance.store,
                    category=1
                )
    
    def update_product_and_code(self, instance, item_ids):
        for item in instance.orderitem_set.all():
            if item.id in item_ids:
                product_store = StoreProduct.objects.filter(id=item.product_id).first()
                if product_store.sell == True:
                    product_store.sell = False
                    product_store.quantity = 1
                    product_store.save()
                else:
                    product_store.quantity += 1
                    product_store.save()
                code_product = ProductCode.objects.filter(code=item.code).first()
                code_product.sell = False
                code_product.save()
    
    def create_history_order_return(self, instance, item_ids):
        order_items = instance.orderitem_set.filter(id__in=item_ids)
        for item in order_items:
            ReturnOrderHistory.objects.create(
                order=item.order,
                product=item.product,
                code=item.code,
                price=item.price
            )
        
class OrderCreateSerializers(serializers.ModelSerializer):
    client_firstname = serializers.CharField(write_only=True, required=False)
    client_lastname = serializers.CharField(write_only=True, required=False)
    client_surname = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    client_phonenumber = serializers.CharField(write_only=True, required=False)
    address = serializers.CharField(write_only=True, required=False)
    products = OrderItemCreateSerializers(many=True, write_only=True)
    
    class Meta:
        model = Order
        fields = ('client', 'price_type', 'delivery', 'status',
                  'comment', 'client', 'currency', 'user', 'delivery_user', 
                  'store', 'seller', 'client_firstname', 'client_lastname', 'client_surname',
                  'client_phonenumber', 'discount_amount', 'discount_percentage', 'products', 'address')
    
    def validate(self, attrs):
        price = 0
        discount_amount  = attrs['discount_amount']
        for data in attrs['products']:
            if not ProductCode.objects.filter(code=data['code']).first():
                raise serializers.ValidationError("Введите валидный штрих-код")
            price += data['price']
        if discount_amount and discount_amount < 0:
            raise serializers.ValidationError("Неверная сумма скидки")
        if discount_amount and (price * 70 / 100) < discount_amount:
            raise serializers.ValidationError("Скидка не должна превышать 70%")
        elif not price:
            raise serializers.ValidationError("Цена не включена")
        attrs['discount_amount'] = attrs.get('discount_amount', 0)
        attrs['discount_percentage'] = attrs.get('discount_percentage', 0)
        return super().validate(attrs)
    
    @transaction.atomic
    def create(self, validated_data):
        try:
            products_data = validated_data.pop('products', [])
            validated_data = self.create_client(validated_data)
            discount_price, price = self.calculate_price(products_data, validated_data)
            validated_data.update({'price': price})
            instance = super().create(validated_data)
            self.record_store_balance(products_data, discount_price, instance)
            self.update_client_cashback(instance, discount_price)
            self.apply_discounts_for_client(instance)
            self.create_product(products_data, instance)
            
            order_image = self.generate_order_image(instance, float(discount_price)*float(instance.currency.exchange_rate))
            order_image.save(settings.MEDIA_ROOT+"invoice/modified_invoice.png")
            
            self.send_bot_message(instance, float(discount_price)*float(instance.currency.exchange_rate))
            return instance
        except Exception as e:
            raise serializers.ValidationError({"non_field_errors": [f"Произошла ошибка при сохранении: {e}"]})
    @transaction.atomic
    def update(self, instance, validated_data):
        products_data = validated_data.pop('products', [])
        
        instance.store = validated_data.get('store', instance.store)
        instance.client = validated_data.get('client', instance.client)
        instance.price = validated_data.get('price', instance.price)
        instance.discount_amount = validated_data.get('discount_amount', instance.discount_amount)
        instance.discount_percentage = validated_data.get('discount_percentage', instance.discount_percentage)
        instance.price_type = validated_data.get('price_type', instance.price_type)
        instance.currency = validated_data.get('currency', instance.currency)
        instance.user = validated_data.get('user', instance.user)
        instance.delivery = validated_data.get('delivery', instance.delivery)
        instance.delivery_user = validated_data.get('delivery_user', instance.delivery_user)
        instance.store = validated_data.get('store', instance.store)
        instance.status = validated_data.get('status', instance.status)
        instance.comment = validated_data.get('comment', instance.comment)
        instance.seller = validated_data.get('seller', instance.seller)
        
        
        discount_price, price = self.calculate_price(products_data, validated_data)
        validated_data.update({'price': price})
        self.record_store_balance(products_data, discount_price, instance)
        self.update_client_cashback(instance, discount_price)
        self.apply_discounts_for_client(instance)
        self.create_product(products_data, instance)
        
        order_image = self.generate_order_image(instance, float(discount_price)*float(instance.currency.exchange_rate))
        order_image.save(settings.MEDIA_ROOT+"invoice/modified_invoice.png")
        
        self.send_bot_message(instance, float(discount_price)*float(instance.currency.exchange_rate))
        return super().update(instance, validated_data)
    
    def create_client(self, validated_data):
        client_firstname = validated_data.pop('client_firstname', None)
        client_lastname = validated_data.pop('client_lastname', None)
        client_surname = validated_data.pop('client_surname', None)
        client_phonenumber = validated_data.pop('client_phonenumber', None)
        address = validated_data.pop('address', None)

        if not validated_data.get('client'):
            client = Client.objects.create(
                first_name=client_firstname,
                last_name=client_lastname,
                surname=client_surname,
                address=address,
                phone_number1=client_phonenumber
            )
            validated_data['client'] = client
        elif address:
            client = validated_data.get('client')
            client.address = address
            client.save()
        return validated_data
    
    def calculate_price(self, products_data, validated_data):
        price = 0
        for product in products_data:
            price += product['price']
        if validated_data['discount_amount'] and validated_data['discount_percentage']:
            return price - (price * validated_data['discount_percentage'] / 100) - validated_data['discount_amount'], price
        elif validated_data['discount_percentage']:
            return price - ((price * validated_data['discount_percentage']) / 100), price
        elif validated_data['discount_amount']:
            return price - validated_data['discount_amount'], price
        return price, price
    
    def record_store_balance(self, products_data, price, instance):
        codes = [products['code'] for products in products_data]
        s_price = 0
        cost = 0
        for product in products_data:
            s_price += product['product'].reception.price
            cost += product['product'].reception.price
        s_price = price - s_price
        if instance.status == 2:
            StoreBalance.objects.create(
                debit=price,
                profit=s_price,
                cost=cost,
                description=f"Продажа - {'-'.join(codes)}",
                store=instance.store,
                category=1
            )
    
    def create_product(self, products, instance):
        instance.orderitem_set.all().delete()
        for product in products:
            OrderItem.objects.create(
                order = instance,
                product = product['product'],
                code = product['code'],
                price = product['price'],
            )
            self.update_product_and_code(product['product'], product['code'], instance)
    
    def update_client_cashback(self, instance, price):
        if instance.status == 2:
            setting = Settings.objects.last()
            client_cash = Cashback.objects.filter(client=instance.client).first()
            if client_cash:
                if instance.discount_amount and client_cash.amount >= instance.discount_amount:
                    client_cash.amount -= instance.discount_amount
                elif instance.discount_amount and client_cash.amount <= instance.discount_amount:
                    client_cash.amount = 0
                client_cash.amount += Decimal(price) * Decimal(setting.product_discount) / 100
                client_cash.save()
            else:
                Cashback.objects.create(client=instance.client, amount=Decimal(price) * Decimal(setting.product_discount) / 100)
            instance.cashback_price = Decimal(price) * Decimal(setting.product_discount) / 100
            instance.save()
    
    def update_product_and_code(self, product, code, instance):
        product_store = StoreProduct.objects.filter(id=product.id, store=instance.store, sell=False).first()
        if product_store.quantity == 1:
            product_store.sell = True
            product_store.save()
        else:
            product_store.quantity -= 1
            product_store.save()
        code_product = ProductCode.objects.filter(code=code, store=instance.store, sell=False).first()
        code_product.sell = True
        code_product.save()
        
    def apply_discounts_for_client(self, instance):
        if instance.status == 2:
            discounts = DiscountLevel.objects.all().order_by('-id')
            
            for discount_data in discounts:
                end_date = timezone.now()
                start_date = end_date - timedelta(days=int(discount_data.month) * 31)
                
                orders_price = Order.objects.filter(
                    client=instance.client,
                    created_at__range=(start_date, end_date)
                ).aggregate(total_price=Sum('price'))['total_price'] or 0
                if orders_price >= discount_data.limit:
                    discount_client = Discount.objects.filter(client=instance.client).first()
                    if discount_client and discount_client.level_id == discount_data.id:
                        break
                    if discount_client and discount_client.type == True:
                        break
                    if discount_client:
                        discount_client.level = discount_data
                        discount_client.status = False
                        discount_client.save()
                        break
                    else:
                        Discount.objects.create(
                            level=discount_data,
                            client=instance.client,
                            status=False
                        )
                        break

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

    def send_bot_message(self, order, price):
        price_type_display = dict(Type.choices).get(order.price_type)
        message =  f"\nКассир: {order.user.firstname}"\
            f"\nКлиент: {order.client.first_name} {order.client.last_name} {order.client.phone_number1}"\
            f"\nЦена (сум): {self.price_format(round(price))} сум"\
            f"\nТип оплаты: {price_type_display}"\
            f"\nМагазин: {order.store.name}"\
            f"\nПродавец: {order.seller.firstname}"\
            f"\nДата: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        a = 1
        for item in order.orderitem_set.all():
            message += f"{a}. {item.product.reception.product.name} {item.product.reception.region.name}"\
                f"\nКод: {item.code}"
            a += 1
        if order.client.chat_id:
            bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))
            try:
                return bot.send_message(order.client.chat_id, message)
            except:
                pass
        return 1

    def price_format(self, inp):
        try:
            price = int(inp)
            res = "{:,}".format(price)
            formated = re.sub(",", " ", res)
            return formated
        except: 
            return inp
  
class AmoCrmOrderSerializers(serializers.Serializer):
    name = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone_number = serializers.CharField()
    price = serializers.CharField()
    type = serializers.IntegerField()
    month = serializers.IntegerField(required=False)
    delivery = serializers.CharField()

class OrderCommentSerializers(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'comment')