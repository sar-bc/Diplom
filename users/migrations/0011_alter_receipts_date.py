# Generated by Django 5.0.6 on 2024-08-01 00:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_alter_receipts_options_remove_receipts_kv'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receipts',
            name='date',
            field=models.DateField(verbose_name='За какой месяц'),
        ),
    ]
