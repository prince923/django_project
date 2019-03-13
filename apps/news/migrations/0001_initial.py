# Generated by Django 2.1.7 on 2019-03-13 15:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=True, verbose_name='逻辑删除')),
                ('content', models.TextField(help_text='评论内容', verbose_name='评论内容')),
                ('author', models.ForeignKey(help_text='评论作者', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='评论作者')),
            ],
            options={
                'verbose_name': '新闻评论',
                'verbose_name_plural': '新闻评论',
                'db_table': 'tb_comments',
                'ordering': ['-update_time', '-id'],
            },
        ),
        migrations.CreateModel(
            name='NewsBanner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=True, verbose_name='逻辑删除')),
                ('image_url', models.URLField(help_text='轮播图图片链接', verbose_name='轮播图图片链接')),
                ('priority', models.IntegerField(default=6, help_text='轮播图片优先级', verbose_name='轮播图片优先级')),
            ],
            options={
                'verbose_name': '新闻轮播图',
                'verbose_name_plural': '新闻轮播图',
                'db_table': 'news_banner',
                'ordering': ['priority', '-update_time', '-id'],
            },
        ),
        migrations.CreateModel(
            name='NewsHots',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=True, verbose_name='逻辑删除')),
                ('priority', models.IntegerField(default=3, help_text='新闻优先级', verbose_name='新闻优先级')),
            ],
            options={
                'verbose_name': '新闻优先级',
                'verbose_name_plural': '新闻优先级',
                'db_table': 'tb_news_hots',
                'ordering': ['-update_time', '-id'],
            },
        ),
        migrations.CreateModel(
            name='NewsModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=True, verbose_name='逻辑删除')),
                ('title', models.CharField(help_text='新闻标题', max_length=150, verbose_name='新闻标题')),
                ('digest', models.CharField(help_text='新闻摘要', max_length=200, verbose_name='新闻摘要')),
                ('content', models.TextField(help_text='新闻内容', verbose_name='新闻内容')),
                ('clicks', models.IntegerField(default=0, help_text='新闻点击量', verbose_name='新闻点击量')),
                ('image_url', models.URLField(default='', help_text='图片url', verbose_name='图片url')),
                ('author', models.ForeignKey(help_text='新闻作者', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='新闻作者')),
            ],
            options={
                'verbose_name': '新闻',
                'verbose_name_plural': '新闻',
                'db_table': 'tb_news',
                'ordering': ['-update_time', '-id'],
            },
        ),
        migrations.CreateModel(
            name='TagModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_delete', models.BooleanField(default=True, verbose_name='逻辑删除')),
                ('tag_name', models.CharField(help_text='新闻标签名', max_length=64, verbose_name='新闻标签名')),
            ],
            options={
                'verbose_name': '新闻标签',
                'verbose_name_plural': '新闻标签',
                'db_table': 'tb_tag',
                'ordering': ['-update_time', '-id'],
            },
        ),
        migrations.AddField(
            model_name='newsmodel',
            name='tag',
            field=models.ForeignKey(help_text='新闻标签', null=True, on_delete=django.db.models.deletion.SET_NULL, to='news.TagModel', verbose_name='新闻标签'),
        ),
        migrations.AddField(
            model_name='newshots',
            name='news',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='news.NewsModel'),
        ),
        migrations.AddField(
            model_name='newsbanner',
            name='news',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='news.NewsModel'),
        ),
        migrations.AddField(
            model_name='commentmodel',
            name='news',
            field=models.ForeignKey(help_text='评论新闻', on_delete=django.db.models.deletion.CASCADE, to='news.NewsModel', verbose_name='评论新闻'),
        ),
        migrations.AddField(
            model_name='commentmodel',
            name='parents',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='news.CommentModel'),
        ),
    ]
