from django.views.generic import TemplateView
from apps.articles.models import Article, Section, NAVIGATE_SECTIONS


class IndexView(TemplateView):
    template_name = 'articles/index.html'

    def get_context_data(self, **kwargs):
        kwargs.update(
            sections=Section.objects.filter(slug__in=NAVIGATE_SECTIONS).order_by('id'),
            marquee=Article.objects.filter(section__slug='news').order_by('-publish_date').first(),
            news_list=Article.objects.filter(section__slug='news').order_by('?')[:3]  # order by vote_sum?
        )
        return super().get_context_data(**kwargs)


class SectionView(TemplateView):
    template_name = 'articles/index.html'


class RssView(TemplateView):
    template_name = 'articles/rss.html'
