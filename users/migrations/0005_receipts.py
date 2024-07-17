# Generated by Django 5.0.6 on 2024-07-16 04:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_delete_userimport'),
    ]

    operations = [
        migrations.CreateModel(
            name='Receipts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kv', models.IntegerField(verbose_name='Квартира')),
                ('date', models.DateField(verbose_name='Закакой месяц')),
                ('file', models.FileField(upload_to='receipts/', verbose_name='Квитанция')),
                ('show', models.IntegerField(verbose_name='Кол-во скачиваний')),
            ],
        ),
    ]
