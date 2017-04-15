from apps.authors.models import Author
from apps.articles.models import Notice, Article, Section, NAVIGATE_SECTIONS
from apps.bloggers.models import Entry
from apps.polls.models import Poll


class SidebarContextMixin(object):

    def get_sidebar_context(self):
        return {
            'poll': Poll.objects.order_by('?').first(),
            'sidebar_videos': Article.objects.visible().filter(section__is_video=True)[:2],
            'sidebar_news': Article.objects.visible().filter(is_news=True).order_by('?')[:10],  # order by vote_sum?
            'notices': Notice.objects.filter(status=Notice.STATUS.approved)[:3],
            'entries': Entry.objects.active().order_by('?')[:5],
            'authors': Author.objects.order_by('last_name')[:15],
        }


class HeaderContextMixin(object):

    def get_header_context(self):
        return {
            'header_rating_news': Article.objects.visible().filter(is_news=True).order_by('?')[:3],  # order by vote_sum?
            'marquee': Article.objects.visible().order_by('-publish_date').first(),
            'sections': Section.objects.filter(slug__in=NAVIGATE_SECTIONS).order_by('id'),
        }


class PageContextMixin(HeaderContextMixin, SidebarContextMixin):

    def get_context_data(self, **kwargs):
        kwargs.update(
            self.get_header_context()
        )
        kwargs.update(
            self.get_sidebar_context()
        )
        return super().get_context_data(**kwargs)
