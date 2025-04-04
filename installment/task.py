from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from .models import InstallmentPlan, Debt, Payment
import random
import string
import requests
import threading
import re 

@shared_task
def send_payment_reminder_sms():
    today = timezone.now().date()
    reminders = {
        3: "Hurmatli {client}.\n{date} sanada shartnoma bo‘yicha {price} so'm ({dollor} $ USD) to‘lovingizni borligini eslatib o‘tamiz.\nTo‘lovni o‘z vaqtida amalga oshirishni unutmang.\nTelefon: +998 55 510 50 50",
        2: "Hurmatli {client}.\n{date} sanada shartnoma bo‘yicha {price} so'm ({dollor} $ USD) to‘lovingizni borligini eslatib o‘tamiz.\nTo‘lovni o‘z vaqtida amalga oshirishni unutmang.\nTelefon: +998 55 510 50 50",
        1: "Hurmatli {client}.\n{date} sanada shartnoma bo‘yicha {price} so'm ({dollor} $ USD) to‘lovingizni borligini eslatib o‘tamiz.\nTo‘lovni o‘z vaqtida amalga oshirishni unutmang.\nTelefon: +998 55 510 50 50",
        0: "Hurmatli {client}.\n{date} kuni shartnoma bo‘yicha to‘lov sanangiz, darhol  {price} so'm ({dollor} $ USD) To‘lovni amalga oshirishingizni so‘raymiz, aks holda qurilma bloklanadi.\nTelefon: +998 55 510 50 50"
    }
    for days_before, message in reminders.items():
        payments = InstallmentPlan.objects.filter(next_payment_date=today + timedelta(days=days_before), status=1)
        for payment in payments:
            try:
                payment_client = Payment.objects.filter(installment_plan=payment, due_date=today + timedelta(days=days_before)).first()
                personalized_message = message.format(client=f"{payment.client.first_name} {payment.client.last_name}", 
                                                    date=today + timedelta(days=days_before),
                                                    price=price_format(payment_client.amount * payment.currency.exchange_rate), 
                                                    dollor=payment_client.amount)
                t = threading.Thread(target=send_sms_notification, args=(payment.client.phone_number1, personalized_message))
                t.start()
                t.join()
            except:
                pass
            
    overdue_payments = InstallmentPlan.objects.filter(next_payment_date__lt=today, status=1)
    for payment in overdue_payments:
        try:
            payment_client = Payment.objects.filter(installment_plan=payment, due_date__lt=today, payment_received=False).order_by('-id').first()
            overdue_amount = price_format(payment_client.amount * payment.currency.exchange_rate)
            existing_debt = Debt.objects.filter(installment=payment, client=payment.client, due_date=payment_client.due_date).first()
            
            if not existing_debt:
                Debt.objects.create(
                    installment=payment,
                    client=payment.client,
                    outstanding_amount=payment_client.amount,
                    due_date=payment_client.due_date,
                )
            message = f"{payment.client.first_name} {payment.client.last_name}.\nSizda {payment_client.due_date} sanadan {overdue_amount} sum ({payment_client.amount} $ USD) qarzdorlik mavjud.{payment_client.due_date + timedelta(days=15)} gacha  qarzdorlik zudlik bilan qoplanmasa, sud tartibida majburiy undirishga qaratilishi haqida ogohlantiramiz.\nTelefon: +998 55 510 50 50"
            t = threading.Thread(target=send_sms_notification, args=(payment.client.phone_number1, message))
            t.start()
            t.join()
        except:
            pass 
            
def send_sms_notification(phone_number, message):
    code = ''.join(random.choice(string.digits) for _ in range(4))
    url = "http://sms.etc.uz:8084/single-sms"
    header = {'Content-Type': 'application/json'}
    body = {
        "header": {
            "login": "",
            "pwd": "",
            "CgPN": ""
        },
        "body": {
            "message_id_in": f"{code}",
            "CdPN": phone_number[1:],
            "text": f"{message}"
        }
    }
    requests.post(url=url, json=body, headers=header)
    
    
def price_format(inp):
        try:
            price = int(inp)
            res = "{:,}".format(price)
            formated = re.sub(",", " ", res)
            return formated
        except: 
            return inp