from rest_framework import serializers
from .models import (
    PlanMonth, 
    InstallmentPlan, 
    InstallmentProduct,
    Payment,
    Debt
    )
from reception.models import StoreProduct, ProductCode, Reception
from reception.serializers import StoreProductSerializers
from client.models import Cashback
from product.models import Settings, Type
from client.serializers import ClientListSerializers
from store.models import StoreBalance, PriceList
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from currency.serializers import CurrencySerializers
from django.utils import timezone
from django.db.models import F, Sum
from user.serializers import UserListSerializers

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
    
class MonthSerializers(serializers.ModelSerializer):
    class Meta:
        model = PlanMonth
        fields = "__all__"

class InstallmentProductSerializers(serializers.ModelSerializer):
    class Meta:
        model = InstallmentProduct
        fields = ('id', 'product', 'code', 'price')
        
class InstallmentReturnSerializers(serializers.ModelSerializer):
    amount = serializers.FloatField(required=False)
    class Meta:
        model = InstallmentPlan
        fields = ('id', 'return_price', 'return_comment', 'amount')
    
    def validate(self, attrs):
        if not attrs['return_price'] or \
            not attrs['return_comment'] or\
               not attrs['amount'] :
                raise serializers.ValidationError("Введите данные полностью")
        return super().validate(attrs)
    
    def update(self, instance, validated_data):
        amount = validated_data.pop('amount')
        validated_data.update({'status': 6})
        instance = super().update(instance, validated_data)
        for product in instance.installemt_product.all():
            original_reception = Reception.objects.get(id=product.product.reception_id)
            original_reception.pk = None
            original_reception.price = validated_data['return_price']
            original_reception.total_price = validated_data['return_price']
            original_reception.type = Type.objects.filter(name='B/U').first()
            original_reception.status = 1
            original_reception.comment = "Возврат рассрочку"
            original_reception.save()
            
            price = PriceList.objects.filter(store_id=original_reception.store_id, type_id=original_reception.type_id,
                                            brand_id=original_reception.product.brand_id, category=original_reception.product.category_id).first()
            price_sell = original_reception.price
            if price:
                if original_reception.store.type == 2:
                    price_sell = price.price + original_reception.price
                else:
                    price_sell = (original_reception.price * price.percentage / 100) + original_reception.price
                
            StoreProduct.objects.create(
                reception=original_reception,
                store=original_reception.store,
                quantity=original_reception.count,
                price=float(price_sell)
            )
            
            StoreBalance.objects.create(
                credit=float(original_reception.total_price) if amount > 0 else None,
                debit=float(original_reception.total_price) if amount < 0 else None,
                description = f"Возврат рассрочку",
                store = original_reception.store,
                category=3
            )
            ProductCode.objects.filter(reception=original_reception, 
                                       code=product.code).update(sell=False)
            
        return instance
        
class InstallmentProductShortSerializers(serializers.ModelSerializer):
    product = StoreProductSerializers()
    class Meta:
        model = InstallmentProduct
        fields = ('id', 'product', 'code', 'price')
        
class InstallmentCreateSerializers(serializers.ModelSerializer):
    products = InstallmentProductSerializers(many=True, write_only=True)
    class Meta:
        model = InstallmentPlan
        fields = (
            'id',
            'client',
            'store',
            'first_payment',
            'month',
            'discount_amount',
            'discount_percentage',
            'comment',
            'currency',
            'products',
            'seller',
            'user',
        )
    
    def validate(self, attrs):
        if not attrs['client'] or \
            not attrs['first_payment'] or \
                not attrs['month'] or \
                        not attrs['products'] :
            raise serializers.ValidationError("Введите данные полностью")
        for data in attrs['products']:
            if not ProductCode.objects.filter(code=data['code']).first():
                raise serializers.ValidationError("Введите валидный штрих-код")
        if attrs['discount_amount'] and (attrs['first_payment'] * 70 / 100) < attrs['discount_amount']:
            raise serializers.ValidationError("Скидка не должна превышать 70%")
        return super().validate(attrs)

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        amount, total_amount = self.calculate_price(products_data, validated_data)
        validated_data.update({'total_amount': total_amount, 'first_payment': amount})
        instance = super().create(validated_data)
        self.create_product(instance, products_data)
        self.record_balance(amount, instance)
        self.create_payment_month(instance, total_amount)
        self.update_client_cashback(instance, amount)
        return instance
    
    def update(self, instance, validated_data):
        products_data = validated_data.pop('products')
        
        instance.client = validated_data.get('client', instance.client)
        instance.store = validated_data.get('store', instance.store)
        instance.remaining_price = validated_data.get('remaining_price', instance.remaining_price)
        instance.first_payment = validated_data.get('client', instance.client)
        instance.discount_amount = validated_data.get('discount_amount', instance.discount_amount)
        instance.discount_percentage = validated_data.get('discount_percentage', instance.discount_percentage)
        instance.comment = validated_data.get('comment', instance.comment)
        instance.currency = validated_data.get('currency', instance.currency)
        instance.seller = validated_data.get('seller', instance.seller)
        instance.user = validated_data.get('user', instance.user)
        
        amount, total_amount = self.calculate_price(products_data, validated_data)
        
        validated_data.update({'total_amount': total_amount, 
                               'status': 1, 
                               'remaining_month': validated_data['month'].months, 
                               'remaining_price': (total_amount - amount) * (1 + Decimal(validated_data['month'].percentage) / 100),
                               'next_payment_date': timezone.now().date() + relativedelta(months=1)
                               })
        instance = super().update(instance, validated_data)
        self.create_product(instance, products_data)
        self.record_balance(amount, instance)
        self.create_payment_month(instance, total_amount)
        return instance
       
    def calculate_price(self, products_data, validated_data):
        total_price = 0
        for product in products_data:
            total_price += product['price']
        if validated_data['discount_amount'] and validated_data['discount_percentage']:
            return validated_data['first_payment'] - (validated_data['first_payment'] * validated_data['discount_percentage'] / 100) - validated_data['discount_amount'], total_price
        elif validated_data['discount_percentage']:
            return validated_data['first_payment'] - ((validated_data['first_payment'] * validated_data['discount_percentage']) / 100), total_price
        elif validated_data['discount_amount']:
            return validated_data['first_payment'] - validated_data['discount_amount'], total_price
        return validated_data['first_payment'], total_price
        
    def create_product(self, instance, products):
        for product in products:
            InstallmentProduct.objects.create(
                installment = instance,
                product = product['product'],
                code = product['code'],
                price = product['price']
            )
            self.update_product_and_code(product['product'], product['code'], instance)
    
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
        
    def record_balance(self, amount, instance):
        StoreBalance.objects.create(
            debit=amount,
            description=f"первый взнос {instance.client} {instance.created_at.strftime('%Y-%m-%d')}",
            store=instance.store,
            category=3
        )
        
    def create_payment_month(self, instance, total_amount):
        monthly_payment = instance.calculate_installment_amount()
        for i in range(1, instance.month.months+1):
            Payment.objects.create(
                installment_plan=instance,
                amount=monthly_payment,
                due_date=instance.created_at + relativedelta(months=i),
            )
    
    def update_client_cashback(self, instance, price):
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

class PaymentListSerializers(serializers.ModelSerializer):
    # installment_plan = InstallmentPlanListSerializers(read_only=True)
    class Meta:
        model = Payment
        fields = "__all__"
                     
class InstallmentPlanListSerializers(serializers.ModelSerializer):
    products = InstallmentProductShortSerializers(many=True, source='installemt_product')
    client = ClientListSerializers()
    month = serializers.SerializerMethodField()
    installment_amount = serializers.SerializerMethodField()
    payment_info = serializers.SerializerMethodField()
    currency = CurrencySerializers()
    amount = serializers.SerializerMethodField()
    user = UserListSerializers()
    price_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = InstallmentPlan
        fields = (
            'id',
            'client',
            'store',
            'total_amount',
            'first_payment',
            'month',
            'discount_amount',
            'discount_percentage',
            'remaining_month',
            'next_payment_date',
            'products',
            'comment',
            'currency',
            'installment_amount',
            'seller',
            'user',
            'status',
            'amount',
            'payment_info',
            'price_percentage'
        )
    def get_installment_amount(self, obj):
        return obj.calculate_installment_amount()

    def get_amount(self, obj):
        if not obj.status in (4,5):
            return (obj.total_amount - obj.first_payment) * (1 + Decimal(obj.month.percentage) / 100)
        return 0
    
    def get_payment_info(self, obj):
        payments = obj.payments.all().order_by('due_date')
        return PaymentListSerializers(payments, many=True).data

    def get_month(self, obj):
        return {'months': obj.month_str, 'percentage': obj.percentage_str}

    def get_price_percentage(self, obj):
        return (obj.total_amount - obj.first_payment) * obj.percentage_str / 100

class InstallmentPlanIdSerializers(serializers.ModelSerializer):
    class Meta:
        model = InstallmentPlan
        fields = (
            'id',
            'client',
            'store',
            'total_amount',
            'first_payment',
            'month',
            'discount_amount',
            'discount_percentage',
            'remaining_month',
            'next_payment_date',
            'comment',
            'currency',
            'seller',
            'user',
        )
        
class PaymentCreateSerializers(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            'installment_plan',
            'paid_amount',
            'comment'
        )
    
    def validate(self, attrs):
        payments = Payment.objects.filter(installment_plan=attrs['installment_plan'], payment_received=False)
        if payments.__len__() == 1 and not payments[0].amount-payments[0].paid_amount == attrs['paid_amount']:
            raise serializers.ValidationError(f"Последний месяц необходимо закрыть полностью, причитающуюся сумму {payments[0].amount - payments[0].paid_amount}")
        installment_plan = attrs.get('installment_plan')
        paid_amount = attrs.get('paid_amount')

        if installment_plan and paid_amount is not None:
            unpaid_payments = Payment.objects.filter(installment_plan=installment_plan, payment_received=False)
            total_amount_owed = unpaid_payments.aggregate(total_amount=Sum('amount'))['total_amount'] or 0
            if paid_amount > total_amount_owed:
                raise serializers.ValidationError(f"You need to pay the total amount owed, which is {total_amount_owed}.")
        return super().validate(attrs)
    
    def create(self, validated_data):
        instance = self.create_or_update_payments(validated_data)
        self.record_balance(instance)
        self.check_client_debt(instance)
        self.update_client_cashback(validated_data, validated_data['paid_amount'])
        return instance
    
    def create_or_update_payments(self, validated_data):
        installment_plan = validated_data['installment_plan']
        amount = validated_data['paid_amount']
        paid_at = timezone.now()
        payments = Payment.objects.filter(installment_plan=installment_plan, payment_received=False).order_by('due_date')
        
        if payments.__len__() == 1:
            payments[0].paid_amount += amount
            payments[0].payment_received = True
            payments[0].paid_at = paid_at
            payments[0].comment = validated_data['comment']
            payments[0].save()
            return validated_data
        for payment in payments:
            if amount <= 0:
                break
            remaining_amount = payment.amount - payment.paid_amount
            if amount < remaining_amount:
                payment.paid_amount += amount
                payment.paid_at = paid_at
                payment.comment = validated_data['comment']
                if payments.last().id != payment.id:
                    payment.payment_received = True
                    payment.paid_at = paid_at
                elif payments.last().id == payment.id and payments.last().amount == amount:
                     payment.payment_received = True
                     payment.paid_at = paid_at
                payment.save()

                next_payment = payments.filter(payment_received=False).exclude(id=payment.id).first()
                if next_payment:
                    next_payment.amount += remaining_amount - amount
                    next_payment.save()
                    debt = Debt.objects.filter(installment=next_payment.installment_plan, client=next_payment.installment_plan.client, payment_received=False).first()
                    if debt:
                        debt.outstanding_amount += remaining_amount - amount
                        debt.save()
                    else:
                        Debt.objects.create(
                            installment=next_payment.installment_plan,
                            client=next_payment.installment_plan.client,
                            outstanding_amount=remaining_amount - amount,
                            payment_received=False,
                            due_date=payment.due_date
                        )
                break
            else:
                amount -= remaining_amount
                payment.paid_amount = payment.amount
                payment.comment = validated_data['comment']
                if payments.last().id != payment.id:
                    payment.payment_received = True
                    payment.paid_at = paid_at
                elif payments.last().id == payment.id and payments.last().amount == amount:
                     payment.payment_received = True
                     payment.paid_at = paid_at
                payment.save()

                installment_plan.remaining_month -= 1
                installment_plan.remaining_price -= payment.amount

        if payments.filter(payment_received=False).exists():
            next_payment = payments.filter(payment_received=False).first()
            installment_plan.next_payment_date = next_payment.due_date
        else:
            last_payment = payments.last()
            if last_payment:
                installment_plan.next_payment_date = last_payment.due_date + relativedelta(months=1)
            else:
                installment_plan.next_payment_date = None


        installment_plan.save()

        if not payments.filter(payment_received=False).exists():
            installment_plan = validated_data['installment_plan']
            installment_plan.status = 2
            installment_plan.save()

        return validated_data
    
    def record_balance(self, validated_data):
        StoreBalance.objects.create(
            debit=validated_data['paid_amount'],
            profit=validated_data['paid_amount'] * validated_data['installment_plan'].month.percentage / 100,
            cost=validated_data['paid_amount'] - (validated_data['paid_amount'] * validated_data['installment_plan'].month.percentage / 100),
            description=f"Платеж рассрочку {validated_data['installment_plan'].client}",
            store=validated_data['installment_plan'].store,
            category=3
        )
    
    def check_client_debt(self, validated_data):
        debts = Debt.objects.filter(installment=validated_data['installment_plan'], payment_received=False).order_by('due_date')
        paid_amount = validated_data['paid_amount']

        for debt in debts:
            if paid_amount >= debt.outstanding_amount:
                paid_amount -= debt.outstanding_amount
                debt.paid_amount = debt.outstanding_amount
                debt.payment_received = True
            else:
                debt.paid_amount = paid_amount
                paid_amount = 0

            debt.save()

            if paid_amount <= 0:
                break
            
    def update_client_cashback(self, validated_data, price):
        setting = Settings.objects.last()
        client_cash = Cashback.objects.filter(client=validated_data['installment_plan'].client).first()
        if client_cash:
            client_cash.amount += price * Decimal(setting.product_discount) / 100
            client_cash.save()
        else:
            Cashback.objects.create(client=validated_data['installment_plan'].client, amount=price * Decimal(setting.product_discount) / 100)
        
class DebtSerializers(serializers.ModelSerializer):
    installment = InstallmentPlanListSerializers()
    client = ClientListSerializers()
    
    class Meta:
        model = Debt
        fields = "__all__"
        
class DebtUpdateSerializers(serializers.ModelSerializer):
    class Meta:
        model = Debt
        fields = ('id', 'comment')
        
class InstallmentStatusSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = InstallmentPlan
        fields = (
            'id',
            'status',
            'seller'
        )
        
class InstallmentCommentSerializers(serializers.ModelSerializer):

    class Meta:
        model = InstallmentPlan
        fields = (
            'id',
            'comment'
        )