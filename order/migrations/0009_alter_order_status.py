# Generated by Django 4.1.5 on 2024-06-06 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0008_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.IntegerField(choices=[(0, 'None'), (1, 'В ожидании'), (2, 'оплаты'), (3, 'закрыт'), (4, 'Новый'), (5, 'Заказать'), (6, 'Возврат')], default=0),
        ),
    ]
