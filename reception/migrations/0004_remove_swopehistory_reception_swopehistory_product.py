# Generated by Django 5.0.4 on 2024-04-10 00:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reception', '0003_swopehistory'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='swopehistory',
            name='reception',
        ),
        migrations.AddField(
            model_name='swopehistory',
            name='product',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='reception.storeproduct'),
        ),
    ]
