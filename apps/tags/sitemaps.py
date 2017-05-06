from django.contrib.sitemaps import Sitemap
from apps.tags.models import Tag


class TagSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.8

    def items(self):
        return Tag.objects.order_by('-updated_at')

    def lastmod(self, obj):
        return obj.updated_at
