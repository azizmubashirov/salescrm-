# Generated by Django 5.0.4 on 2024-05-10 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_remove_product_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]
