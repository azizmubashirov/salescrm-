import django_filters
from .models import StoreProduct

class StoreProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='max_price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='max_price', lookup_expr='lte')

    class Meta:
        model = StoreProduct
        fields = ['reception__product', 'reception__color', 'reception__region',
                  'reception__ram', 'reception__memory', 'reception__type',
                  'reception__product__brand', 'reception__currency']