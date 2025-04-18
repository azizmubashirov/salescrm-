# Generated by Django 4.1.5 on 2024-07-08 21:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('currency', '0003_currency_is_main'),
        ('installment', '0012_remove_installmentplan_margin_percentage_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='installmentplan',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='installmentplan',
            name='currency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='currency.currency'),
        ),
    ]
