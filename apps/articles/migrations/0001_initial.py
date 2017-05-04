# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-04 20:10
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('authors', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('content', models.TextField(blank=True, verbose_name='Содержание')),
                ('is_news', models.BooleanField(default=False, verbose_name='Новость')),
                ('author_names', models.CharField(blank=True, help_text='Список внешних авторов через запятую', max_length=255, verbose_name='Авторы')),
                ('publish_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата публикации')),
                ('is_active', models.BooleanField(default=True)),
                ('source', models.CharField(blank=True, max_length=255, verbose_name='Источник')),
                ('source_link', models.URLField(blank=True, verbose_name='Ссылка на источник')),
                ('discussion_status', models.CharField(choices=[('open', 'Открыто'), ('close', 'Закрыто')], default='open', max_length=8, verbose_name='Статус обсуждения')),
                ('status', models.CharField(choices=[('new', 'Новая'), ('approved', 'Одобрена')], default='new', max_length=8, verbose_name='Статус')),
                ('show_comments', models.BooleanField(default=True, verbose_name='Показывать комментарии')),
                ('comments_count', models.PositiveIntegerField(default=0, editable=False, verbose_name='Кол-во комментариев')),
                ('image', models.ImageField(blank=True, max_length=255, null=True, upload_to='articles_image', verbose_name='Картинка')),
                ('video', models.URLField(blank=True, verbose_name='Ссылка на видео')),
                ('thumbnail', models.CharField(blank=True, max_length=200, verbose_name='Ссылка на превью')),
                ('rating', models.FloatField(default=0, editable=False, verbose_name='Рейтинг')),
                ('vote_count', models.PositiveIntegerField(default=0, editable=False, verbose_name='Кол-во проголосовавших')),
                ('authors', models.ManyToManyField(blank=True, to='authors.Author', verbose_name='Авторы')),
            ],
            options={
                'verbose_name_plural': 'Статьи',
                'ordering': ('-pk',),
                'verbose_name': 'Статья',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(blank=True, max_length=40, verbose_name='Идентификатор')),
                ('username', models.CharField(max_length=255, verbose_name='Имя')),
                ('title', models.CharField(blank=True, max_length=255, verbose_name='Заголовок')),
                ('content', models.TextField(verbose_name='Содержание')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('is_active', models.BooleanField(default=True)),
                ('karma', models.IntegerField(default=0, editable=False, verbose_name='Оценка')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articles.Article', verbose_name='Статья')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='articles.Comment', verbose_name='Родительский комментарий')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Комментарии',
                'ordering': ('-pk',),
                'verbose_name': 'Комментарий',
            },
        ),
        migrations.CreateModel(
            name='Multimedia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.URLField(blank=True, verbose_name='Ссылка на youtube')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articles.Article', verbose_name='Статья')),
            ],
            options={
                'verbose_name_plural': 'Мультимедиа',
                'ordering': ('-pk',),
                'verbose_name': 'Мультимедиа',
            },
        ),
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('content', models.CharField(max_length=200, verbose_name='Содержание')),
                ('status', models.CharField(choices=[('new', 'Новый'), ('approved', 'Одобрен')], default='new', max_length=8, verbose_name='Статус')),
            ],
            options={
                'verbose_name_plural': 'Анонсы',
                'ordering': ('-pk',),
                'verbose_name': 'Анонс',
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('slug', models.CharField(max_length=255, unique=True, verbose_name='Слаг')),
                ('is_video', models.BooleanField(default=False)),
                ('channel', models.CharField(blank=True, help_text='Идентификатор канала на youtube', max_length=100, verbose_name='Канал')),
                ('is_active', models.BooleanField(default=True)),
                ('ext_id', models.IntegerField(db_index=True, default=0, editable=False, verbose_name='Внешний ID')),
            ],
            options={
                'verbose_name_plural': 'Разделы',
                'ordering': ('-pk',),
                'verbose_name': 'Раздел',
            },
        ),
        migrations.AddField(
            model_name='article',
            name='section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='articles.Section', verbose_name='Раздел'),
        ),
    ]
