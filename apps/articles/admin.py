from django.contrib import admin
from apps.articles.models import Section, Article


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_active')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'publish_date', 'is_active', 'comments_count')
