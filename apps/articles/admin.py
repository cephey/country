from django.contrib import admin
from django.db import models

from apps.articles.models import Section, Article, Notice, Comment
from apps.articles.forms import AdminArticleForm, AdminNoticeForm


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_video', 'is_active')
    list_filter = ('is_active', 'is_video')

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'channel')
        }),
        ('Переключатели', {
            'fields': ('is_active', 'is_video')
        }),
    )


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    form = AdminArticleForm
    list_display = ('title', 'is_active', 'is_video', 'section', 'publish_date', 'comments_count')
    list_select_related = ('section',)
    list_filter = ('is_active', 'section')
    fieldsets = (
        (None, {
            'fields': ('title', 'section')
        }),
        ('Тело статьи', {
            'fields': ('description', 'content')
        }),
        ('Переключатели', {
            'fields': ('is_active', 'is_news', 'show_comments', 'status', 'discussion_status')
        }),
        ('Дополнительно', {
            'fields': ('publish_date', 'authors', 'author_names', 'source', 'source_link')
        }),
        ('Изображения и видео', {
            'fields': ('image', 'video')
        }),
    )

    def is_video(self, obj):
        return obj.section.is_video
    is_video.short_description = 'is video'
    is_video.boolean = True


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'article', 'subject')
    list_select_related = ('article',)
    readonly_fields = ('article', 'owner', 'created_at')
    fieldsets = (
        (None, {
            'fields': ('article', 'owner')
        }),
        ('Основная информация', {
            'fields': ('username', 'title', 'content')
        }),
        ('Дополнительно', {
            'fields': ('is_active', 'created_at')
        }),
    )

    def subject(self, obj):
        return obj.subject
    subject.short_description = 'Содержание'

    def owner(self, obj):
        if obj.user:
            return obj.user.display()
        if obj.token:
            return 'Аноним: {}'.format(obj.token)
    owner.short_description = 'Владелец'


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    form = AdminNoticeForm
    list_display = ('__str__', 'status')
    list_filter = ('status',)
    fields = ('content', 'status')
