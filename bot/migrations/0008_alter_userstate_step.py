# Generated by Django 5.0.6 on 2024-08-22 22:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0007_rename_user_userstate_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userstate',
            name='step',
            field=models.IntegerField(default=10),
        ),
    ]
