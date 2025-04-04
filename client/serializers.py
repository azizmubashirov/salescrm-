from rest_framework import serializers
from client.models import Client, Discount, Cashback, DiscountLevel
from typing import Dict
from decimal import Decimal
from order.models import Order
from currency.models import Currency
from django.db.models import Sum

class ClientSerializers(serializers.ModelSerializer):
    passport_file = serializers.CharField(write_only=True, required=False, allow_blank=True)
    class Meta:
        model = Client
        fields = ('id', 'first_name', 'last_name', 'surname', 'phone_number1', 'phone_number2', 'passport_file', 
                  'comment', 'address', 'address2', 'status', 'chat_id')
        
class ClientBotSerializers(serializers.Serializer):
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    phone_number1 = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    chat_id = serializers.CharField(write_only=True, required=False)
        
    def create(self, validated_data):
        client = Client.objects.filter(phone_number1=validated_data['phone_number1']).first()
        if not client:
            return Client.objects.create(**validated_data)
        client.chat_id = validated_data['chat_id']
        client.save()
        return client
    
class ClientListSerializers(serializers.ModelSerializer):
    level = serializers.SerializerMethodField()
    cashback = serializers.SerializerMethodField()
    order_price = serializers.SerializerMethodField()
    class Meta:
        model = Client
        fields = "__all__"
        
    def get_level(self, obj: Client) -> list[str]:
        discount_levels = Discount.objects.filter(client=obj, status=True).first()
        if not discount_levels:
            return {}
        levels = {'name': discount_levels.level.name, 'percentage': discount_levels.level.discount_percentage, 'percentage_installment': discount_levels.level.discount_percentage_installment}
        return levels
    
    def get_cashback(self, obj: Client) -> Decimal:
        latest_cashback = Cashback.objects.filter(client=obj).first()
        if not latest_cashback:
            return Decimal(0)
        return latest_cashback.amount
    
    def get_order_price(self, obj: Client):
        orders_price = Order.objects.filter(
            client=obj,
        ).aggregate(total_price=Sum('price'))['total_price'] or 0
        return orders_price

class ClientShortSerializers(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('id', 'first_name', 'last_name', 'surname')

class ClientDeleteSerializers(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of ids",
        max_length=100
    )

    def validate_ids(self, value):
        if not value:
            raise serializers.ValidationError("Id is not provided")
        return value
    

class DiscountLevelSerializers(serializers.ModelSerializer):
    class Meta:
        model = DiscountLevel
        fields = "__all__"

class CLientLevelSerializers(serializers.ModelSerializer):
    client = ClientShortSerializers()
    level = DiscountLevelSerializers()
    class Meta:
        model = Discount
        fields = "__all__"
        
class CLientLevelUpdateSerializers(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ('status', )

class ClientlevelCreateSerializers(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ('id', 'client', 'level', 'status')
        
    def create(self, validated_data):
        validated_data['type'] = True
        return super().create(validated_data)