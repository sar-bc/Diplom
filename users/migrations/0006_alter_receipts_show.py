# Generated by Django 5.0.6 on 2024-07-16 05:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_receipts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receipts',
            name='show',
            field=models.IntegerField(default=0, verbose_name='Кол-во скачиваний'),
        ),
    ]
