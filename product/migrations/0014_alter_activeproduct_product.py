# Generated by Django 4.1.5 on 2024-07-07 16:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0013_activeproduct'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activeproduct',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='active_product', to='product.product'),
        ),
    ]
