# Generated by Django 5.0.6 on 2024-08-12 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UsersBot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('username', models.CharField(max_length=100)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('ls', models.IntegerField()),
                ('kv', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Пользователи бота',
                'verbose_name_plural': 'Пользователи бота',
            },
        ),
    ]
