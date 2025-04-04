from django.db import models
from client.models import Client
from reception.models import StoreProduct
from currency.models import Currency
from user.models import User
from store.models import Store


class Status(models.IntegerChoices):
    NONE = 0, 'None'
    PAID = 1, 'В ожидании'
    PAYMENT = 2, 'оплаты'
    CLOSED = 3, 'закрыт'
    BOT = 4, 'Новый'
    BOT_ORDER = 5, 'Заказать'
    RETURN = 6, 'Возврат'
   
class Type(models.IntegerChoices):
    NONE = 0, 'None'
    PAID = 1, 'Наличные'
    TERMINAL = 2, 'терминал'
    TRANSFER = 3, 'перевод' 

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        
class Order(BaseModel):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_percentage = models.IntegerField(blank=True, null=True)
    price_type = models.IntegerField(choices=Type.choices, default=Type.NONE)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="user_order")
    delivery = models.BooleanField(default=False)
    delivery_user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, blank=True, null=True)
    status = models.IntegerField(choices=Status.choices, default=Status.NONE)
    comment = models.TextField(blank=True, null=True)
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="seller")
    cashback_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        ordering = ['-id']
        db_table = 'order'
        
    def __str__(self) -> str:
        return f"{self.client} {self.price}"
    
class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(StoreProduct, on_delete=models.CASCADE, related_name='order_prodcut')
    code = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    class Meta:
        ordering = ['-id']
        db_table = 'order_item'
    
    def __str__(self) -> str:
        return f"{self.order} {self.product} {self.code}"
    
class ReturnOrderHistory(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_return_hostory')
    product = models.ForeignKey(StoreProduct, on_delete=models.CASCADE, related_name='order_prodcut_return_history')
    code = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    class Meta:
        ordering = ['-id']
        
    def __str__(self) -> str:
        return f"{self.order} {self.product} {self.code}"