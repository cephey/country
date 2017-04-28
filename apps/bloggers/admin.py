from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from apps.bloggers.models import Blogger, Entry


@admin.register(Blogger)
class BloggerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'link_url', 'is_active')

    def link_url(self, obj):
        return format_html('<a href="{url}">{url}</a>', url=obj.link)
    link_url.short_description = _('Ссылка на блог')


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'blogger', 'link_url', 'is_active')
    list_select_related = ('blogger',)
    readonly_fields = ('title', 'description', 'blogger', 'link_url', 'created_at')
    fields = ('title', 'blogger', 'description', 'link_url', 'is_active', 'created_at')

    def link_url(self, obj):
        return format_html('<a href="{url}">{url}</a>', url=obj.link)
    link_url.short_description = _('Ссылка на запись')
