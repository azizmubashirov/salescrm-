# Generated by Django 4.1.5 on 2024-07-10 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('installment', '0020_debt_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='installmentplan',
            name='first_payment',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
