# Generated by Django 2.1.7 on 2019-03-15 03:20

from django.db import migrations
import user.models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='usermodel',
            managers=[
                ('objects', user.models.UserManager()),
            ],
        ),
    ]
