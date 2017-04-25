from datetime import timedelta
from itertools import chain

from django.db.models import Case, When, Value, IntegerField
from django.utils import timezone
from django.views.generic import TemplateView, DetailView
from django.shortcuts import get_object_or_404

from apps.articles.views import BaseArticleListView
from apps.articles.models import Article, Section, Comment, NAVIGATE_SECTIONS, GENERIC_SECTIONS, BEST, NEWS, VIDEO
from apps.articles.forms import CommentForm
from apps.utils.mixins.views import PdaPageContextMixin
from apps.utils.mixins.paginator import PaginatorMixin


class IndexView(PdaPageContextMixin, TemplateView):
    template_name = 'pda/index.html'

    def get_context_data(self, **kwargs):
        sections = Section.objects.navigate()

        main_news = list(Article.objects.visible()
                         .filter(is_news=True)
                         .order_by('-publish_date')[:5])

        main_material = (Article.objects.visible()
                         .filter(is_news=False)
                         .order_by('-publish_date', '-comments_count')
                         .first())

        exclude_ids = {article.id for article in main_news} | {main_material.id}

        materials = []
        for section in sections:
            article = Article.objects.visible().filter(section=section).exclude(id__in=exclude_ids).first()
            exclude_ids.add(article.id)
            materials.append((section, article))

        article = Article.objects.visible().filter(is_news=True).exclude(id__in=exclude_ids).first()
        materials.insert(0, (GENERIC_SECTIONS[NEWS], article))

        kwargs.update(
            main_news=main_news[0],
            last_news=[main_material] + main_news[1:],
            materials=materials
        )
        return super().get_context_data(**kwargs)


class SectionView(BaseArticleListView):
    section = None

    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        if slug in GENERIC_SECTIONS:
            self.section = GENERIC_SECTIONS[slug]
        else:
            self.section = get_object_or_404(Section.objects.active(), slug=slug)
        return super().get(request, *args, **kwargs)

    def get_ordering(self):
        if self.section.slug == BEST:
            return '-rating', '-vote_count', '-id'
        return super().get_ordering()

    def get_queryset(self):
        qs = super().get_queryset().visible()
        if self.section.slug == BEST:
            return qs.filter(publish_date__gt=timezone.now() - timedelta(days=7))
        elif self.section.slug == NEWS:
            return qs.filter(is_news=True)
        elif self.section.slug == VIDEO:
            return qs.filter(section__is_video=True)
        return qs.filter(section=self.section)

    def get_context_data(self, **kwargs):
        kwargs.update(
            partition=self.section,
            nav_section=None if self.section.slug in GENERIC_SECTIONS else self.section
        )
        return super().get_context_data(**kwargs)


class ArticleDetailView(PdaPageContextMixin, PaginatorMixin, DetailView):
    template_name = 'articles/detail.html'
    queryset = Article.objects.visible().select_related('section').prefetch_related('multimedia_set')
    section = None

    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        if slug in GENERIC_SECTIONS:
            self.section = GENERIC_SECTIONS[slug]
        else:
            self.section = Section.objects.active().filter(slug=slug).first()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update(
            art_section=self.section or self.object.section,
            comment_form=CommentForm()
        )
        if self.object.show_comments:
            comments = Comment.objects.filter(article=self.object, is_active=True)
            kwargs['art_comments'] = self.paginate_qs(comments, 3)
        else:
            data = []
            for slug in NAVIGATE_SECTIONS:
                article = (Article.objects.visible()
                           .filter(section__slug=slug)
                           .select_related('section')
                           .order_by('-publish_date')
                           .first())
                if article:
                    data.append(article)
            kwargs['in_sections'] = data
        return super().get_context_data(**kwargs)
