from django.contrib import admin
from apps.articles.models import Section, Article, Notice


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_active')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'publish_date', 'is_active', 'comments_count')


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status')
    list_filter = ('status',)
