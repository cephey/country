# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-03 20:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Blogger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('first_name', models.CharField(blank=True, max_length=255, verbose_name='Имя')),
                ('last_name', models.CharField(blank=True, max_length=255, verbose_name='Фамилия')),
                ('middle_name', models.CharField(blank=True, max_length=255, verbose_name='Отчество')),
                ('link', models.CharField(blank=True, max_length=255, verbose_name='Ссылка на блог')),
                ('photo', models.ImageField(blank=True, max_length=255, null=True, upload_to='bloggers', verbose_name='Фото')),
                ('is_active', models.BooleanField(default=True)),
                ('ext_id', models.IntegerField(db_index=True, default=0, editable=False, verbose_name='Внешний ID')),
            ],
            options={
                'verbose_name': 'Блогер',
                'ordering': ('-pk',),
                'verbose_name_plural': 'Блогеры',
            },
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('title', models.CharField(max_length=255, verbose_name='Заголовок')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('link', models.CharField(blank=True, max_length=255, verbose_name='Ссылка на запись')),
                ('publish_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата публикации')),
                ('is_active', models.BooleanField(default=True)),
                ('blogger', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bloggers.Blogger', verbose_name='Блогер')),
            ],
            options={
                'verbose_name': 'Запись',
                'ordering': ('-pk',),
                'verbose_name_plural': 'Записи',
            },
        ),
    ]
