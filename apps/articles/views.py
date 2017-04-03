from django.http import Http404
from django.db.models import Count, Avg
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.views.generic import TemplateView, ListView, DetailView, RedirectView
from django.core.paginator import InvalidPage, Paginator

from apps.articles.models import Article, Section, Comment
from apps.votes.models import Vote
from apps.utils.mixins.views import HeaderContextMixin, SidebarContextMixin
from apps.utils.mixins.paginator import PaginatorMixin


class IndexView(HeaderContextMixin, SidebarContextMixin, TemplateView):
    template_name = 'articles/index.html'

    def get_context_data(self, **kwargs):
        kwargs.update(
            main_news=Article.objects.filter(is_news=True).order_by('-publish_date').first(),
            main_material=Article.objects.order_by('-publish_date', '-comments_count').first(),

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


class ArticleView(HeaderContextMixin, SidebarContextMixin, PaginatorMixin, DetailView):
    template_name = 'articles/detail.html'
    model = Article

    def get_context_data(self, **kwargs):
        kwargs['art_votes'] = (Vote.objects
                               .filter(object_id=self.object.id,
                                       content_type=ContentType.objects.get_for_model(Article))
                               .aggregate(count=Count('id'), avg=Avg('score')))

        comments = Comment.objects.filter(article=self.object, is_active=True)
        kwargs['art_comments'] = self.paginate_qs(comments, 3)

        kwargs.update(
            self.get_header_context()
        )
        kwargs.update(
            self.get_sidebar_context()
        )
        return super().get_context_data(**kwargs)


class ActionView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return self.request.META.get('HTTP_REFERER')

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class RssView(TemplateView):
    template_name = 'articles/rss.html'
