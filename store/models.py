from django.db import models
from product.models import Product, Type, Brand, Category, Color, Region

class StoreType(models.IntegerChoices):
    NONE = 0, '----'
    PERCENTAGE = 1, 'Процент'
    Sum = 2, 'Сумма'

class BalanceCategory(models.IntegerChoices):
    OTHER = 0, 'Другой'
    ORDER = 1, 'Продажа'
    RECEPTION = 2, 'Прием'
    INSTALLMENT = 3, 'Рассрочка'
    BROCAST = 4, 'Передача'
    INVEST = 5, 'Инвестиция'

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Store(BaseModel):
    name = models.CharField(max_length=150, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    type = models.IntegerField(choices=StoreType.choices, default=StoreType.NONE)
    sell_price = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'store'
        ordering = ['-id']
    
    def __str__(self) -> str:
        return f"{self.name}"
    
class SwopeStore(BaseModel): 
    from_store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='from_store_swope')
    to_store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='to_store_swope')


class StoreBalance(BaseModel):
    debit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    profit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    credit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.IntegerField(choices=BalanceCategory.choices, default=BalanceCategory.OTHER)
    store = models.ForeignKey(
        Store, on_delete=models.DO_NOTHING,
        related_name="balance_store"
    )
    
    @property
    def balance(self):
        return (self.debit or 0) - (self.credit or 0)
    
    def __str__(self):
        return '%s (%s)' % (self.debit, self.credit)

    class Meta:
        verbose_name = "store_balance"
        verbose_name_plural = "store_balance"
        ordering = ["-created_at", ]
        
        
class PriceList(BaseModel):
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE,
        related_name="price_store"
    )
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, blank=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, blank=True, null=True)
    ram = models.IntegerField(default=0)
    memory = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    percentage = models.IntegerField(default=0)
    
