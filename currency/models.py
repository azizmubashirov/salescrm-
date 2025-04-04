from django.db import models


class DateModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Currency(DateModel):
    name = models.CharField(max_length=100, blank=True, null=True)
    symbol = models.CharField(max_length=120, blank=True, null=True)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_main = models.BooleanField(default=False, null=True, blank=True)
    
    class Meta:
        ordering = ['-id']
        db_table = 'currency'
    
    def __str__(self):
        return f"{self.symbol}"
        
class CurrencyHistory(models.Model):
    currency = models.ForeignKey(Currency, related_name='history', on_delete=models.CASCADE)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.currency} - {self.exchange_rate} - {self.timestamp}"