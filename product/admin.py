from django.contrib import admin
from product.models import Settings, Category, Brand, Product

admin.site.register(Settings)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Product)
