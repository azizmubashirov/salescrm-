from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from django.contrib.postgres.fields import ArrayField
from datetime import datetime
from text_unidecode import unidecode
from django.utils.text import slugify

def create_title_slug(instance):
    slug = instance.slug
    if slug is None or slug == "":
        slug = slugify(unidecode(instance.name_uz))
    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        if Klass.objects.get(slug=slug).pk != instance.pk:
            slug = slugify("{}-{}".format(unidecode(instance.name_uz), datetime.now().timestamp()))
    return slug

def create_title_brand_slug(instance):
    slug = instance.slug
    if slug is None or slug == "":
        slug = slugify(unidecode(instance.name))
    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        if Klass.objects.get(slug=slug).pk != instance.pk:
            slug = slugify("{}-{}".format(unidecode(instance.name), datetime.now().timestamp()))
    return slug

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Type(BaseModel):
    name = models.CharField(max_length=100, blank=False, null=False)
    
    class Meta:
        db_table = 'type'
        ordering = ['-id']
    
    def __str__(self) -> str:
        return f"{self.name}"


class Brand(BaseModel):
    name = models.CharField(max_length=100, null=False, blank=False)
    image = models.URLField(blank=True, null=True, max_length=500)
    slug = models.SlugField(unique=True, max_length=355, allow_unicode=True, null=True, blank=True)
    
    class Meta:
        ordering = ['-id']
    
    def __str__(self) -> str:
        return f"{self.name}"

    def save(self, *args, **kwargs):
        self.slug = create_title_brand_slug(self)
        return super().save(*args, **kwargs)
    
class Category(MPTTModel, BaseModel):
    image = models.URLField(blank=True, null=True, max_length=500)
    name_uz = models.CharField(max_length=100, blank=False, null=False)
    name_ru = models.CharField(max_length=100, blank=True, null=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    is_home = models.BooleanField(default=False, null=False)
    is_popular = models.BooleanField(default=False, null=False)
    slug = models.SlugField(unique=True, max_length=355, allow_unicode=True, null=True, blank=True)
    
    class MPTTMeta:
        order_insertion_by = ['id']
        ordering = ['-id']
        db_table = 'category'
    
    def __str__(self) -> str:
        return f"{self.name_uz}"

    def save(self, *args, **kwargs):
        self.slug = create_title_slug(self)
        return super().save(*args, **kwargs)
    
class Product(BaseModel):
    name = models.CharField(max_length=100, blank=False, null=False)
    image = ArrayField(models.JSONField(blank=True, null=True, default=dict), blank=True, default=list)
    brand = models.ForeignKey(to=Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE)
    parent_category = models.ForeignKey(to=Category, on_delete=models.SET_NULL, blank=True, null=True, related_name="product_parent_category")
    description_uz = models.TextField(blank=True, null=True)
    description_ru = models.TextField(blank=True, null=True)
    is_popular = models.BooleanField(default=False, null=False)
    
    class Meta:
        db_table = 'product'
        ordering = ['-id']
    
    def __str__(self) -> str:
        return f"{self.name}"
    

class ActiveProduct(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="active_product")
    status = models.BooleanField(default=False)
    
    
class Region(BaseModel):
    name = models.CharField(max_length=150, null=True, blank=True)
    
    class Meta:
        db_table = 'region'
        ordering = ['-id']
    
    def __str__(self) -> str:
        return f"{self.name}"
    
class Color(BaseModel):
    name_uz = models.CharField(max_length=100)
    name_ru = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'color'
        ordering = ['-id']
    
    def __str__(self) -> str:
        return f"{self.name_uz}"


class Settings(BaseModel):
    product_discount = models.FloatField(blank=True, null=True)
    first_payment_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    