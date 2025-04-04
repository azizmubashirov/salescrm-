from django.db import models
from django.utils import timezone
from client.models import Client
from reception.models import StoreProduct
from store.models import Store
from datetime import timedelta
from decimal import Decimal
from currency.models import Currency
from user.models import User
from dateutil.relativedelta import relativedelta

class Status(models.IntegerChoices):
    NONE = 0, '---'
    PAID = 1, 'Активный'
    PAYMENT = 2, 'Завершенный'
    BOT = 4, 'Новый'
    BOT_ORDER = 5, 'Заказать'
    RETURN = 6, 'Возврат'
    

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        
class PlanMonth(BaseModel):
    months = models.PositiveIntegerField()
    percentage = models.IntegerField(default=0)
    
    def __str__(self) -> str:
        return f"{self.months} - {self.percentage}"

class InstallmentPlan(BaseModel):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='installment_plans')
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    remaining_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    first_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    month = models.ForeignKey(PlanMonth, on_delete=models.SET_NULL, blank=True, null=True)
    month_str = models.IntegerField(blank=False, null=False, default=0)
    percentage_str =  models.IntegerField(blank=False, null=False, default=0)
    remaining_month = models.PositiveIntegerField(blank=True, null=True)
    next_payment_date = models.DateField(blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    discount_percentage = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(choices=Status.choices, default=Status.NONE)
    comment = models.TextField(blank=True, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, blank=True, null=True)
    return_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    return_comment = models.TextField(blank=True, null=True)
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="ins_seller")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="user_ins")

    def calculate_installment_amount(self):
        if self.total_amount and self.first_payment and self.month_str and self.percentage_str:
            return (self.total_amount - self.first_payment) * (1 + Decimal(self.percentage_str) / 100) / self.month_str
        else:
            return 0

    def __str__(self):
        return f"Installment Plan for {self.client.first_name} - {self.month} months"

    def save(self, *args, **kwargs):
        if not self.pk and not self.status in (4,5):
            self.next_payment_date = timezone.now().date() + relativedelta(months=1)
            self.remaining_month = self.month.months
            self.remaining_price = (self.total_amount - self.first_payment) * (1 + Decimal(self.month.percentage) / 100)
            self.status = 1
            self.month_str = self.month.months
            self.percentage_str = self.month.percentage
        super().save(*args, **kwargs)

class InstallmentProduct(BaseModel):
    installment = models.ForeignKey(InstallmentPlan, on_delete=models.CASCADE, related_name="installemt_product")
    product = models.ForeignKey(StoreProduct, on_delete=models.CASCADE, related_name='plan_prodcut')
    code = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

class Payment(BaseModel):
    installment_plan = models.ForeignKey(InstallmentPlan, on_delete=models.CASCADE, related_name='payments')
    due_date = models.DateField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    paid_at = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True, null=True)
    payment_received = models.BooleanField(default=False)
    
    def is_overdue(self):
        return self.due_date < timezone.now().date() and self.paid_at is None

    def __str__(self):
        return f"Payment of {self.amount} for {self.installment_plan.client.first_name}"
    
    def save(self, *args, **kwargs):
        super(Payment, self).save(*args, **kwargs)

class Debt(BaseModel):
    installment = models.ForeignKey(InstallmentPlan, on_delete=models.CASCADE, related_name="installemt_debt")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='debts')
    outstanding_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    due_date = models.DateField()
    payment_received = models.BooleanField(default=False)
    received_at = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Debt of {self.outstanding_amount} for {self.client.first_name} due on {self.due_date}"
