# Generated by Django 5.0.4 on 2024-05-13 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0005_discountlevel_cashback_discount'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='barcode',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='tab_number',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
