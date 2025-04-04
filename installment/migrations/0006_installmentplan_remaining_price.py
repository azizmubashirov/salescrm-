# Generated by Django 4.1.5 on 2024-06-26 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('installment', '0005_installmentplan_store'),
    ]

    operations = [
        migrations.AddField(
            model_name='installmentplan',
            name='remaining_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
    ]
