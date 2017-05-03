from cacheback.base import Job as CachebackJob
from apps.articles.models import Article, Section, Notice
from apps.authors.models import Author
from apps.bloggers.models import Entry
from apps.polls.models import Poll


class Job(CachebackJob):
    lifetime = 300  # 5 minutes
    cache_ttl = 24 * 3600  # 1 day
    fetch_on_miss = True


class SidebarContextJob(Job):

    def fetch(self):
        return {
            'poll': Poll.objects.active().prefetch_related('choice_set').order_by('?').first(),
            'sidebar_videos': (Article.objects.visible()
                               .select_related('section')
                               .filter(section__is_video=True)[:2]),
            'sidebar_news': Article.objects.visible().filter(is_news=True).order_by('?')[:10],  # order by vote_sum?
            'notices': Notice.objects.filter(status=Notice.STATUS.approved)[:3],
            'entries': Entry.objects.active().select_related('blogger').order_by('-publish_date')[:5],
            'authors': Author.objects.order_by('last_name')[:15],
        }


class HeaderContextJob(Job):

    def fetch(self):
        return {
            'header_rating_news': Article.objects.visible().filter(is_news=True).order_by('?')[:3],  # order by vote_sum?
            'marquee': Article.objects.visible().select_related('section').order_by('-publish_date').first(),
            'sections': Section.objects.navigate()
        }
