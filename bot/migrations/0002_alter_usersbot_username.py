# Generated by Django 5.0.6 on 2024-08-12 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersbot',
            name='username',
            field=models.CharField(blank=True, default=None, max_length=100),
        ),
    ]