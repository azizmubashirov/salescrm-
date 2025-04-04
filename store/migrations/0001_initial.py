# Generated by Django 5.0.4 on 2024-04-09 17:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(blank=True, max_length=150, null=True)),
                ('address', models.CharField(blank=True, max_length=100, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=100, null=True)),
                ('swope', models.ManyToManyField(blank=True, null=True, to='store.store')),
            ],
            options={
                'db_table': 'store',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='PriceList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('price', models.FloatField(blank=True, null=True)),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.brand')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.category')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.type')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_store', to='store.store')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StoreBalance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('debit', models.IntegerField(blank=True, default=0)),
                ('credit', models.IntegerField(blank=True, default=0)),
                ('description', models.TextField(blank=True, null=True)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='balance_store', to='store.store')),
            ],
            options={
                'verbose_name': 'store_balance',
                'verbose_name_plural': 'store_balance',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='StoreProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('quantity', models.IntegerField(blank=True, null=True)),
                ('price', models.FloatField(blank=True, null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.store')),
            ],
            options={
                'db_table': 'store_product',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='SwopeHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.BooleanField(default=False)),
                ('from_store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_store', to='store.store')),
                ('to_store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_store', to='store.store')),
            ],
            options={
                'db_table': 'swope_history',
                'ordering': ['-id'],
            },
        ),
    ]
