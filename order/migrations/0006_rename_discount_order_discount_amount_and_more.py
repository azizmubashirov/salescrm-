# Generated by Django 5.0.4 on 2024-05-13 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_order_discount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='discount',
            new_name='discount_amount',
        ),
        migrations.AddField(
            model_name='order',
            name='discount_percentage',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
