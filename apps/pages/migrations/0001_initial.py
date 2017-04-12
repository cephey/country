# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-12 20:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('logo', models.ImageField(blank=True, max_length=255, null=True, upload_to='pages', verbose_name='Логотип')),
                ('url', models.CharField(blank=True, max_length=255, verbose_name='Адрес')),
                ('rating', models.PositiveIntegerField(default=0, verbose_name='Рейтинг')),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('-pk',),
                'verbose_name_plural': 'Сайты',
                'verbose_name': 'Сайт',
            },
        ),
        migrations.CreateModel(
            name='ResourceType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Название')),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('-pk',),
                'verbose_name_plural': 'Типы',
                'verbose_name': 'Тип',
            },
        ),
        migrations.AddField(
            model_name='resource',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pages.ResourceType', verbose_name='Тип'),
        ),
    ]
