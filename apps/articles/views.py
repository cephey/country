from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from apps.articles.models import Article, Section
from apps.utils.mixins.views import HeaderContextMixin, SidebarContextMixin


class IndexView(HeaderContextMixin, SidebarContextMixin, TemplateView):
    template_name = 'articles/index.html'

    def get_context_data(self, **kwargs):
        kwargs.update(
            main_news=Article.objects.filter(section__slug='news').order_by('-publish_date').first(),
            main_material=Article.objects.filter(section__slug='best').order_by('-publish_date').first(),

            materials={
                'politic': Section.objects.get(slug='politic'),
                'moscow': Section.objects.get(slug='moscow'),
                'economic': Section.objects.get(slug='economic'),
                'region': Section.objects.get(slug='region'),
                'society': Section.objects.get(slug='society'),
                'power': Section.objects.get(slug='power'),
                'fpolitic': Section.objects.get(slug='fpolitic'),
                'kompromat': Section.objects.get(slug='kompromat'),
            },
        )
        # 6 articles for each section
        # order by data (+ shuffle)
        kwargs.update(
            self.get_header_context()
        )
        kwargs.update(
            self.get_sidebar_context()
        )
        return super().get_context_data(**kwargs)


class SectionView(HeaderContextMixin, SidebarContextMixin, ListView):
    template_name = 'articles/section.html'
    paginate_by = 20
    model = Article
    section = None

    def get(self, request, *args, **kwargs):
        self.section = get_object_or_404(Section, slug=kwargs.get('slug'))
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(section=self.section)

    def get_context_data(self, **kwargs):
        kwargs['active_section'] = self.section
        kwargs.update(
            self.get_header_context()
        )
        kwargs.update(
            self.get_sidebar_context()
        )
        return super().get_context_data(**kwargs)


class RssView(TemplateView):
    template_name = 'articles/rss.html'
