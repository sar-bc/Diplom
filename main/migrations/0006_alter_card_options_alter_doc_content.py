# Generated by Django 5.0.6 on 2024-08-01 00:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_zayavki_options_alter_zayavki_created_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='card',
            options={'verbose_name': 'Инфо-Карточку', 'verbose_name_plural': 'Инфо-Карточки'},
        ),
        migrations.AlterField(
            model_name='doc',
            name='content',
            field=models.TextField(blank=True, verbose_name='Описание'),
        ),
    ]
