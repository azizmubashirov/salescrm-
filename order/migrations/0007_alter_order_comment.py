# Generated by Django 4.1.5 on 2024-05-29 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0006_rename_discount_order_discount_amount_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
    ]
