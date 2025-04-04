# Generated by Django 4.1.5 on 2024-07-18 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0016_storebalance_cost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storebalance',
            name='category',
            field=models.IntegerField(choices=[(0, 'Другой'), (1, 'Продажа'), (2, 'Прием'), (3, 'Рассрочка'), (4, 'Передача'), (5, 'Инвестиция')], default=0),
        ),
    ]
