# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-20 21:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authors', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('title', models.CharField(max_length=255, verbose_name='Имя')),
                ('content', models.TextField(blank=True, verbose_name='Содержание')),
                ('publish_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата публикации')),
                ('is_active', models.BooleanField(default=True)),
                ('comments_count', models.PositiveIntegerField(default=0, editable=False, verbose_name='Кол-во комментариев')),
                ('authors', models.ManyToManyField(blank=True, to='authors.Author')),
            ],
            options={
                'ordering': ('-pk',),
                'verbose_name': 'Статья',
                'verbose_name_plural': 'Статьи',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255, verbose_name='Имя')),
                ('title', models.CharField(blank=True, max_length=255, verbose_name='Заголовок')),
                ('content', models.TextField(verbose_name='Содержание')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('-pk',),
                'verbose_name': 'Комментарий',
                'verbose_name_plural': 'Комментарии',
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Название')),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('-pk',),
                'verbose_name': 'Раздел',
                'verbose_name_plural': 'Разделы',
            },
        ),
        migrations.AddField(
            model_name='article',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articles.Section', verbose_name='Раздел'),
        ),
    ]
