from django.utils import timezone
from django.urls import reverse_lazy
from django.contrib.sitemaps import Sitemap

from apps.articles.models import Article, Section, NEWS


class NewsSection(object):
    """ Fake news section for sitemaps """
    def get_absolute_url(self):
        return reverse_lazy('articles:section', kwargs={'slug': NEWS})


class ArticleSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.8

    def items(self):
        return Article.objects.visible().order_by('-publish_date')

    def lastmod(self, obj):
        return obj.publish_date


class SectionSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.7

    def items(self):
        return [NewsSection()] + list(Section.objects.navigate())

    def lastmod(self, obj):
        return timezone.now()
