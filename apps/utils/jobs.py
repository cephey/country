from cacheback.base import Job as CachebackJob
from apps.articles.models import Article, Section, Notice
from apps.authors.models import Author
from apps.bloggers.models import Entry
from apps.polls.models import Poll
from datetime import timedelta

from django.utils import timezone


class Job(CachebackJob):
    lifetime = 300  # 5 minutes
    cache_ttl = 24 * 3600  # 1 day
    fetch_on_miss = True


def get_last_news(count):
    return (Article.objects.visible()
            .filter(is_news=True)
            .order_by('-publish_date')
            .values_list('id', flat=True)[:count])


class SidebarContextJob(Job):

    def fetch(self):
        return {
            'poll': (Poll.objects.active()
                     .prefetch_related('choice_set')
                     .filter(created_at__gt=timezone.now() - timedelta(days=30))
                     .order_by('?')
                     .first()),
            'sidebar_videos': (Article.objects.visible()
                               .select_related('section')
                               .filter(section__is_video=True)[:2]),
            'sidebar_news': (Article.objects.visible()
                             .filter(id__in=get_last_news(32))
                             .order_by('-rating')[:10]),
            'notices': Notice.objects.filter(status=Notice.STATUS.approved)[:3],
            'entries': Entry.objects.active().select_related('blogger').order_by('-publish_date')[:5],
            'authors': Author.objects.order_by('last_name')[:16],
        }


class HeaderContextJob(Job):

    def fetch(self):
        return {
            'header_rating_news': (Article.objects.visible()
                                   .filter(id__in=get_last_news(16))
                                   .order_by('-rating')[:3]),
            'marquee': (Article.objects.visible()
                        .select_related('section')
                        .filter(is_ticker=True)
                        .order_by('-publish_date')
                        .first()),
            'sections': Section.objects.navigate()
        }
