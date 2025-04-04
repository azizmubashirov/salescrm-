from django.db import models
from product.models import Product, Type, Color
from product.models import Region
from currency.models import Currency
from store.models import Store
from user.models import User
from text_unidecode import unidecode
from django.utils.text import slugify
from datetime import datetime
from django.contrib.postgres.fields import ArrayField

def create_title_slug(instance):
    slug = instance.slug
    if slug is None or slug == "":
        slug = slugify(unidecode(instance.reception.product.name))
    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        if Klass.objects.get(slug=slug).pk != instance.pk:
            slug = slugify("{}-{}".format(unidecode(instance.reception.product.name), datetime.now().timestamp()))
    return slug

class Status(models.IntegerChoices):
    NONE = 0, 'None'
    PAID = 1, 'Оплачен'
    DEBT = 2, 'Долг'
    DEBT_PAID = 3, 'Долг погашен'
  
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        
class Reception(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    ram = models.IntegerField(default=0)
    memory = models.IntegerField(default=0)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    box = models.BooleanField(default=False)
    price  = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_price  = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    full_name = models.CharField(max_length=200)
    count = models.IntegerField(default=0)
    phone_number = models.CharField(max_length=50)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    status = models.IntegerField(choices=Status.choices, default=Status.NONE)
    comment = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'reception'
        ordering = ['-id']
    
    def __str__(self) -> str:
        return f"{self.product}"
        
    
    
class ProductCode(BaseModel):
    reception = models.ForeignKey(Reception, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, blank=True, null=True)
    code = models.CharField(max_length=200)
    sell = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return f"{self.code} -> {self.reception_id}"
    
    

class StoreProduct(BaseModel):
    reception = models.ForeignKey(to=Reception, on_delete=models.CASCADE)
    store = models.ForeignKey(to=Store, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sell = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, max_length=355, allow_unicode=True, null=True, blank=True)
    
    class Meta:
        db_table = 'store_product'
        ordering = ['-id']
        
    def __str__(self) -> str:
        return f"{str(self.reception.product.name)} {str(self.reception.color)} {str(self.reception.ram)}/{str(self.reception.memory)} {str(self.reception.region)}"
    
    def save(self, *args, **kwargs):
        self.slug = create_title_slug(self)
        return super().save(*args, **kwargs)
    

class SwopeHistory(BaseModel):
    from_store = models.ForeignKey(to=Store, on_delete=models.CASCADE, related_name='from_store')
    to_store = models.ForeignKey(to=Store, on_delete=models.CASCADE, related_name="to_store")
    product = models.ForeignKey(StoreProduct, on_delete=models.CASCADE, default=0)
    codes = ArrayField(models.CharField(blank=True, null=True, max_length=200), blank=True, default=list)
    type = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'swope_history'
        ordering = ['-id']
    
    def __str__(self) -> str:
        return f"{self.from_store} -> {self.to_store}"
    