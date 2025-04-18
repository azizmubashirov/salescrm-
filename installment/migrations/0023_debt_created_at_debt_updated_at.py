# Generated by Django 4.1.5 on 2024-08-02 07:48

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('installment', '0022_debt_paid_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='debt',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='debt',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
