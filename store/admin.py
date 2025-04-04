from django.contrib import admin
from .models import Store, StoreBalance, PriceList

admin.site.register(Store)
admin.site.register(StoreBalance)
admin.site.register(PriceList)
