from django.views.generic import TemplateView
from apps.articles.models import Article, Section, NAVIGATE_SECTIONS


class IndexView(TemplateView):
    template_name = 'articles/index.html'

    def get_context_data(self, **kwargs):
        kwargs.update(
            sections=Section.objects.filter(slug__in=NAVIGATE_SECTIONS).order_by('id'),
            marquee=Article.objects.filter(section__slug='news').order_by('-publish_date').first(),
            news_list=Article.objects.filter(section__slug='news').order_by('?')[:3],  # order by vote_sum?

            main_news=Article.objects.filter(section__slug='news').order_by('-publish_date').first(),
            main_material=Article.objects.filter(section__slug='best').order_by('-publish_date').first(),

            materials={
                'politic': Section.objects.filter(slug='politic'),
                'moscow': Section.objects.filter(slug='moscow'),
                'economic': Section.objects.filter(slug='economic'),
                'region': Section.objects.filter(slug='region'),
                'society': Section.objects.filter(slug='society'),
                'power': Section.objects.filter(slug='power'),
                'fpolitic': Section.objects.filter(slug='fpolitic'),
                'kompromat': Section.objects.filter(slug='kompromat'),
            }
        )
        # 6 articles for each section
        # order by data (+ shuffle)
        return super().get_context_data(**kwargs)


class SectionView(TemplateView):
    template_name = 'articles/index.html'


class RssView(TemplateView):
    template_name = 'articles/rss.html'
