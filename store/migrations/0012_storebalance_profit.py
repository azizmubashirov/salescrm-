# Generated by Django 4.1.5 on 2024-07-08 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_store_sell_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='storebalance',
            name='profit',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
