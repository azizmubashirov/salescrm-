# Generated by Django 4.1.5 on 2024-06-23 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('installment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='installmentplan',
            name='discount_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='installmentplan',
            name='discount_percentage',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
