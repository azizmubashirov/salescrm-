# Generated by Django 5.0.4 on 2024-04-09 21:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_remove_store_swope_swopestore'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='swope',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.store'),
        ),
        migrations.DeleteModel(
            name='SwopeStore',
        ),
    ]
