# Generated by Django 4.1.5 on 2024-07-26 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0010_remove_order_code_remove_order_product_orderitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cashback_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
