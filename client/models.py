from django.db import models
from .__init__ import create_tabnumber

class Status(models.IntegerChoices):
    ACTIVE = 1, 'Активный клиент'
    RELIABLE = 2, 'Надежный клиент'
    UNTRUSTED = 3, 'Ненадежный клиент'
   
   
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Client(BaseModel):
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    surname = models.CharField(max_length=150, blank=True, null=True)
    phone_number1 = models.CharField(max_length=30, blank=True, null=True, unique=True)
    phone_number2 = models.CharField(max_length=30, blank=True, null=True)
    passport_file = models.URLField(blank=True, null=True, max_length=500)
    comment = models.TextField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    address2 = models.TextField(blank=True, null=True)
    status = models.IntegerField(choices=Status.choices, default=Status.ACTIVE)
    chat_id = models.BigIntegerField(unique=True, null=True, blank=True)
    tab_number = models.BigIntegerField(null=False, blank=False)
    barcode = models.URLField(blank=True, null=True, max_length=500)

    class Meta:
        ordering = ['-id']
        db_table = 'client'

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} {self.surname}"
    
    def save(self, *args, **kwargs):
        if self.tab_number is None or self.tab_number == "":
            tab_number, barcode = create_tabnumber(self)
            self.tab_number = tab_number
            self.barcode = barcode
        super(Client, self).save(*args, **kwargs)


class DiscountLevel(models.Model):
    name = models.CharField(max_length=100)
    month = models.IntegerField(blank=True, null=True)
    discount_percentage = models.IntegerField(blank=True, null=True)
    discount_percentage_installment = models.IntegerField(blank=True, null=True)
    limit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    class Meta:
        ordering = ['-id']
        db_table = 'discount_level'
    
    def __str__(self) -> str:
        return f"{self.name} {self.discount_percentage}"

class Discount(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    level = models.ForeignKey(DiscountLevel, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    type = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-id']
        db_table = 'discount'
    
    def __str__(self) -> str:
        return f"{self.client} {self.level or None}"

class Cashback(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']
        db_table = 'cashback'
    
    def __str__(self) -> str:
        return f"{self.client} {self.amount} {self.date}"


class Log(models.Model):
    chat_id = models.BigIntegerField(primary_key=True, null=False,)
    messages = models.JSONField(blank=True, null=True, )

    def __str__(self):
        return "#%s" % self.chat_id
    
    class Meta:
        verbose_name = "log"
        verbose_name_plural = "logs"
        db_table = 'logs'