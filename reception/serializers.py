from rest_framework import serializers
from .models import *
from store.models import PriceList, StoreBalance
from product.models import Product, ActiveProduct
from product.serializers import *
from currency.serializers import *
from store.serializers import StoreSerializers
from typing import List
import barcode
from barcode.writer import ImageWriter
import random
import string
import math

class ReceptionCreateSerializers(serializers.ModelSerializer):
    codes = serializers.ListField(write_only=True, required=False)
    sell_price = serializers.IntegerField(write_only=True, required=False)
    barcode_count = serializers.IntegerField(write_only=True, required=False)
    class Meta:
        model = Reception
        fields = ('id', 'product', 'region', 'currency', 'color', 'ram', 'memory', 
                  'type', 'box', 'price', 'full_name', 'count', 'phone_number',
                  'store', 'status', 'comment', 'codes', 'sell_price', 'barcode_count', 'user')      
    def validate(self, attrs):
        price = PriceList.objects.filter(store_id=attrs['store'], 
                                        type_id=attrs['type'],
                                        product=attrs['product'], 
                                        region=attrs['region'],
                                        color=attrs['color'],
                                        ram=attrs['ram'],
                                        memory=attrs['memory']
                                        ).first()
        if not attrs['price']:
            raise serializers.ValidationError('Цена не включена')
        if not attrs.get('codes', []) or len(attrs.get('codes', [])) <= 0:
            raise serializers.ValidationError('Введите штрих-код')
        if attrs['barcode_count'] and attrs['barcode_count'] > 500:
            raise serializers.ValidationError('Максимальное количество штрих-кода не должна превышать 500')
        elif not price:
            raise serializers.ValidationError('Установите маржу')
        return super().validate(attrs)
    
    def create(self, validated_data):
        codes_data = validated_data.pop('codes', [])
        sell_price_data = validated_data.pop('sell_price', 0)
        barcode_count_data = int(validated_data.pop('barcode_count', 0))
        validated_data['count'] = barcode_count_data if barcode_count_data else validated_data['count']
        price = validated_data.get('price', 0)
        count = validated_data.get('count', 0)
        total_price = price * count
        validated_data['total_price'] = total_price
        reception = super().create(validated_data)
        if barcode_count_data:
            for i in range(1, barcode_count_data+1):
                ProductCode.objects.create(reception=reception, 
                                           code=codes_data[0], 
                                           store=reception.store)
        else:
            for code in codes_data:
                ProductCode.objects.create(reception=reception, 
                                           code=code, 
                                           store=reception.store)
        if sell_price_data:
            price = sell_price_data
        else:
            price = PriceList.objects.filter(store_id=reception.store_id, type_id=reception.type_id,
                                            product=reception.product, color=reception.color,
                                            region=reception.region, ram=reception.ram, 
                                            memory=reception.memory
                                            ).first()
            if price:
                if reception.store.type == 2:
                    price = price.price + reception.price
                else:
                    price = (reception.price * price.percentage / 100) + reception.price
            else:
                price = reception.price
        price = price
        StoreProduct.objects.create(
            reception=reception,
            store=reception.store,
            quantity=reception.count,
            price=price
        )
        if reception.status == 1:
            StoreBalance.objects.create(
                credit=math.ceil(reception.total_price),
                description = f"Прием {reception.product.name} - {reception.count} - {reception.store} - {reception.phone_number}",
                store = reception.store,
                category=2    
            )
        ac_product = ActiveProduct.objects.filter(product=validated_data['product']).first()
        
        if ac_product:
            ac_product.status = True
            ac_product.save()
        else:
            ActiveProduct.objects.create(
                product=validated_data['product'],
                status = True
            )
        return reception
    
class ReceptionUpdateStatusSerializers(serializers.ModelSerializer):
    class Meta:
        model = Reception
        fields = ('id', 'status')
        
    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        StoreBalance.objects.create(
            credit=instance.total_price,
            description = f"Прием Долг погашен {instance.product.name} - {instance.count} - {instance.store} - {instance.phone_number}",
            store = instance.store,
            category=2
        )
        return instance

class ReceptionUpdateSerializers(serializers.ModelSerializer):
    class Meta:
        model = Reception
        fields = ('id', 'region', 'phone_number', 'color', 'ram', 'memory', 'full_name')

class ReceptionSerializers(serializers.ModelSerializer):
    codes = serializers.SerializerMethodField()
    product = ProductListSerializers(read_only=True)
    region = RegionSerializers(read_only=True)
    currency = CurrencySerializers(read_only=True)
    color = ColorSerializers(read_only=True)
    type = TypeSerializers(read_only=True)
    store = StoreSerializers(read_only=True)
    price_sum = serializers.SerializerMethodField()
    total_price_sum = serializers.SerializerMethodField()
    class Meta:
        model = Reception
        fields = ('id', 'product', 'region', 'currency', 'color', 'ram', 'memory', 
                  'type', 'box', 'price', 'total_price', 'full_name', 'count', 'phone_number',
                  'store', 'status', 'comment', 'codes', 'price_sum', 'total_price_sum', 'user')
        
    def get_codes(self, obj: Reception) -> List[str]:
        return [code.code for code in obj.productcode_set.filter(sell=False)]

    def get_price_sum(self, obj: Reception):
        return obj.price * obj.currency.exchange_rate

    def get_total_price_sum(self, obj: Reception):
        return obj.total_price * obj.currency.exchange_rate
    
class ReceptionSerializers2(serializers.ModelSerializer):
    codes = serializers.SerializerMethodField()
    product = ProductListSerializers(read_only=True)
    region = RegionSerializers(read_only=True)
    currency = CurrencySerializers(read_only=True)
    color = ColorSerializers(read_only=True)
    type = TypeSerializers(read_only=True)
    store = StoreSerializers(read_only=True)
    price_sum = serializers.SerializerMethodField()
    total_price_sum = serializers.SerializerMethodField()
    class Meta:
        model = Reception
        fields = ('id', 'product', 'region', 'currency', 'color', 'ram', 'memory', 
                  'type', 'box', 'price', 'total_price', 'full_name', 'count', 'phone_number',
                  'store', 'status', 'comment', 'codes', 'price_sum', 'total_price_sum', 'user')
        
    def get_codes(self, obj: Reception) -> List[str]:
        return [code.code for code in obj.productcode_set.filter()]

    def get_price_sum(self, obj: Reception):
        return obj.price * obj.currency.exchange_rate

    def get_total_price_sum(self, obj: Reception):
        return obj.total_price * obj.currency.exchange_rate

class ReceptionDetailSerializers(serializers.ModelSerializer):
    codes = serializers.SerializerMethodField()
    code_ids = serializers.SerializerMethodField()
    class Meta:
        model = Reception
        fields = ('id', 'product', 'region', 'currency', 'color', 'ram', 'memory', 
                  'type', 'box', 'price', 'total_price', 'full_name', 'count', 'phone_number',
                  'store', 'status', 'comment', 'codes', 'user', 'code_ids')
        
    def get_codes(self, obj: Reception) -> List[str]:
        return [code.code for code in obj.productcode_set.filter(sell=False)]
    
    def get_code_ids(self, obj: Reception) -> List[dict]:
        return [{'code': code.code, 'id': code.id} for code in obj.productcode_set.filter(sell=False)]

class ReceptionReturnSerializers(serializers.ModelSerializer):
    codes = serializers.ListSerializer(child=serializers.CharField(), write_only=True, required=True)
    class Meta:
        model = Reception
        fields = ('codes', )
    
    def update(self, instance, validated_data):
        codes = validated_data.pop('codes', [])
        for code in codes:
            item =ProductCode.objects.filter(id=code).first()
            if item.reception.status == 1 or item.reception.status == 3:
                self.record_balance(item.reception, code)
            if instance.count == 1:
                instance.delete()
            else:
                instance.count -= 1
                instance.save()
                store_product = StoreProduct.objects.filter(reception_id=instance.id, store=item.store).first()
                store_product.quantity -= 1
                store_product.save()
            item.delete()
        return instance
    
    def record_balance(self, instance, code):
        code = ProductCode.objects.filter(id=code).first()
        StoreBalance.objects.create(
            debit=instance.price,
            description = f"Возврат Прием {instance.product.name} - {instance.store} - {instance.phone_number} - {code}",
            store = instance.store,
            category=2
        )
         
class PriceListSerializers(serializers.ModelSerializer): 
    store = StoreSerializers(read_only=True)
    type = TypeSerializers(read_only=True)
    product = ProductListSerializers()
    color = ColorSerializers()
    region = RegionSerializers()
    class Meta:
        model = PriceList
        fields = "__all__"

class PriceSerializers(serializers.ModelSerializer): 
    class Meta:
        model = PriceList
        fields = "__all__"
    def validate(self, attrs):
        price_list = PriceList.objects.filter(store_id=attrs['store'], 
                                              type_id=attrs['type'],
                                              product=attrs['product'],
                                              color=attrs['color'],
                                              region=attrs['region'],
                                              ram=attrs['ram'],
                                              memory=attrs['memory'],
                                              ).first()
        if price_list:
            raise serializers.ValidationError("уже есть маржу")
        return super().validate(attrs)
    

class StoreProductSerializers(serializers.ModelSerializer):
    reception = ReceptionSerializers(read_only=True)
    store = StoreSerializers(read_only=True)
    price = serializers.SerializerMethodField()
    price_sum = serializers.SerializerMethodField()
    code_ids = serializers.SerializerMethodField()
    codes = serializers.SerializerMethodField()
    class Meta:
        model = StoreProduct
        fields = "__all__"
    
    def get_price(self, obj: StoreProduct):
        products = StoreProduct.objects.filter(store=obj.store, reception__product=obj.reception.product, reception__color=obj.reception.color, 
                        reception__ram=obj.reception.ram, reception__memory=obj.reception.memory, sell=False).order_by('-price').first()
        return obj.price if not products else products.price
    
    def get_price_sum(self, obj: StoreProduct):
        products = StoreProduct.objects.filter(store=obj.store, reception__product=obj.reception.product, reception__color=obj.reception.color, 
                        reception__ram=obj.reception.ram, reception__memory=obj.reception.memory, sell=False).order_by('-price').first()
        return obj.price * obj.reception.currency.exchange_rate if not products else products.price * obj.reception.currency.exchange_rate
    
    def get_code_ids(self, obj) -> List[dict]:
        return [{'code': code.code, 'id': code.id} for code in obj.reception.productcode_set.filter(sell=False, store=obj.store)]
    
    def get_codes(self, obj) -> List[str]:
        return [code.code for code in obj.reception.productcode_set.filter(sell=False, store=obj.store)]
    
class StoreProductWebSerializers(serializers.Serializer):
    reception__product = serializers.IntegerField()
    reception__color = serializers.IntegerField()
    reception__region = serializers.IntegerField()
    reception__ram = serializers.IntegerField()
    reception__memory = serializers.IntegerField()
    reception__type = serializers.IntegerField()
    reception__product__brand = serializers.IntegerField()
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2)


class StoreProductEditSerializers(serializers.ModelSerializer):
    class Meta:
        model = StoreProduct
        fields = ('price', )
    
    
      
class SwopeHistorySerializers(serializers.ModelSerializer):
    class Meta:
        model = SwopeHistory
        fields = "__all__"
        
    def validate(self, attrs):
        if not attrs['type']:
            store_product = attrs['product']
            price_list = PriceList.objects.filter(
                store=attrs['to_store'],
                type=store_product.reception.type,
                product=store_product.reception.product,
                color=store_product.reception.color,
                region=store_product.reception.region,
                ram=store_product.reception.ram,
                memory=store_product.reception.memory
            ).first()
            if not price_list:
                raise serializers.ValidationError("В этом магазине нет маржу")
        return super().validate(attrs)
        
    def create(self, validated_data):
        self.update_product(validated_data)
        self.update_product_code(validated_data)
        self.check_product_price(validated_data)
        return super().create(validated_data) 
    
    def check_product_price(self, validated_data):
        if validated_data['type']:
            product = validated_data['product']
            store_product_to_store = StoreProduct.objects.filter(reception=product.reception, store=validated_data['to_store']).first()
            if store_product_to_store:
                store_product_to_store.quantity += validated_data['codes'].__len__()
                store_product_to_store.save()
            else:
                product.pk = None
                product.store = validated_data['to_store']
                product.quantity = validated_data['codes'].__len__()
                product.save()
            
            self.record_balance(validated_data, product.price)
        else:
            store_product = validated_data['product']
            price_list = PriceList.objects.filter(
                store=validated_data['to_store'],
                type=store_product.reception.type,
                product=store_product.reception.product,
                color=store_product.reception.color,
                region=store_product.reception.region,
                ram=store_product.reception.ram,
                memory=store_product.reception.memory
            ).first()
            if not price_list:
                raise serializers.ValidationError("В этом магазине нет маржу")
            if validated_data['to_store'].type == 1:
                price = (store_product.reception.price * price_list.percentage / 100) + store_product.reception.price
            else:
                price = store_product.price + price_list.price
            store_product_to_store = StoreProduct.objects.filter(reception=product.reception, store=validated_data['to_store']).first()
            if store_product_to_store:
                store_product_to_store.quantity += validated_data['codes'].__len__()
                store_product_to_store.save()
            else:
                store_product.pk = None
                store_product.store = validated_data['to_store']
                store_product.quantity = validated_data['codes'].__len__()
                store_product.price = price
                store_product.save()
            self.record_balance(validated_data, price)
    
    def record_balance(self, validated_data, price):
        codes =  validated_data['codes']
        codes = [products.code for products in ProductCode.objects.filter(id__in=codes)]
        StoreBalance.objects.create(
            debit=price,
            description = f'Передача {validated_data["product"].reception.product.name} - {"-".join(codes)}',
            store = validated_data['from_store'],
            category=4
        )
        StoreBalance.objects.create(
            credit=price,
            description = f'Передача {validated_data["product"].reception.product.name} - {"-".join(codes)}',
            store = validated_data['to_store'],
            category=4
        )
    
    def update_product(self, validated_data):
        product = validated_data['product']
        product.quantity -= validated_data['codes'].__len__()
        if product.quantity == 0:
            product.sell = True
        product.save()
        
    def update_product_code(self, validated_data):
        product_code = ProductCode.objects.filter(id__in=validated_data['codes'])
        for code in product_code:
            code.store = validated_data['to_store']
            code.save()
    
class SwopeHistoryListSerializers(serializers.ModelSerializer):
    from_store = StoreSerializers()
    to_store = StoreSerializers()
    product = StoreProductSerializers()
    class Meta:
        model = SwopeHistory
        fields = "__all__"
        

class CreateBarCodeSerializers(serializers.Serializer):
    
    def create(self, validated_data):
        country_code = str(random.choice([str(x) for x in range(450, 461)] + [str(x) for x in range(490, 501)]))
        num = country_code + self.code_generator(size=9)
        ean = barcode.get_barcode_class('ean13')
        book_barcode = ean(num, writer=ImageWriter())
        outputFileFolder = 'media/image/'
        outputFile = outputFileFolder + f'{book_barcode.get_fullcode()}_barcode'
        book_barcode.save(outputFile)
        return {'file': outputFile+".png", 'code': book_barcode.get_fullcode()}
    
    def code_generator(self, size, chars=string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
    

class ReceptionPhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=50)
    full_name = serializers.CharField(max_length=50)
    total_count = serializers.IntegerField()
    

class DeleteSerializers(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of ids",
        max_length=100
    )

    def validate_ids(self, value):
        if not value:
            raise serializers.ValidationError("Id is not provided")
        return value
    
class CodeSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProductCode
        fields = "__all__"