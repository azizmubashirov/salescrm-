from django.contrib import admin
from .models import Client, Cashback, Discount, DiscountLevel

admin.site.register(Client)
admin.site.register(Cashback)
admin.site.register(Discount)
admin.site.register(DiscountLevel)
