# Generated by Django 4.1.5 on 2024-07-08 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reception', '0007_reception_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='storeproduct',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, max_length=355, null=True, unique=True),
        ),
    ]
