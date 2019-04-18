# Generated by Django 2.1.7 on 2019-04-15 03:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='docmodel',
            options={'verbose_name': '文档', 'verbose_name_plural': '文档'},
        ),
        migrations.AlterField(
            model_name='docmodel',
            name='desc',
            field=models.TextField(help_text='文档描述', max_length=200, verbose_name='文档描述'),
        ),
    ]