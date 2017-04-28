from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from apps.pages.models import Partition, Resource


@admin.register(Partition)
class PartitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'partition', 'link_url', 'is_active')
    list_select_related = ('partition',)
    list_filter = ('partition', 'is_active')
    readonly_fields = ('rating', 'created_at')

    def link_url(self, obj):
        return format_html('<a href="{url}">{url}</a>', url=obj.url)
    link_url.short_description = _('Адрес')
