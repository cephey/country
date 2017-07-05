from datetime import timedelta

from django.utils import timezone
from django.views.generic import TemplateView, DetailView, ListView
from django.shortcuts import get_object_or_404

from apps.articles.models import Article, Section, Comment, GENERIC_SECTIONS, BEST, NEWS, VIDEO
from apps.articles.forms import CommentForm
from apps.utils.mixins.views import PdaPageContextMixin
from apps.utils.mixins.paginator import PaginatorMixin


class IndexView(PdaPageContextMixin, TemplateView):
    template_name = 'pda/index.html'

    def get_context_data(self, **kwargs):
        sections = Section.objects.navigate()

        main_news = list(Article.objects.visible()
                         .select_related('section')
                         .filter(is_news=True)
                         .order_by('-publish_date')[:5])

        exclude_ids = {article.id for article in main_news}

        main_material = (Article.objects.visible()
                         .select_related('section')
                         .filter(is_news=False)
                         .order_by('-publish_date', '-comments_count')
                         .first())
        if main_material:
            exclude_ids |= {main_material.id}

        materials = []
        for section in sections:
            article = (Article.objects.visible()
                       .select_related('section')
                       .filter(section=section)
                       .exclude(id__in=exclude_ids)
                       .first())
            exclude_ids.add(article.id)
            materials.append((section, article))

        article = (Article.objects.visible()
                   .select_related('section')
                   .filter(is_news=True)
                   .exclude(id__in=exclude_ids)
                   .first())
        materials.insert(0, (GENERIC_SECTIONS[NEWS], article))

        kwargs.update(
            main_news=main_news[0] if main_news else None,
            last_news=[main_material] + main_news[1:],
            materials=materials
        )
        return super().get_context_data(**kwargs)


class SectionView(PdaPageContextMixin, ListView):
    template_name = 'pda/articles/list.html'
    paginate_by = 5
    queryset = Article.objects.visible().select_related('section')
    page_kwarg = 'p'
    ordering = '-id'
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
            partition=self.section
        )
        return super().get_context_data(**kwargs)


class ArticleDetailView(PdaPageContextMixin, PaginatorMixin, DetailView):
    template_name = 'pda/articles/detail.html'
    queryset = (Article.objects.visible().with_authors()
                .select_related('section')
                .prefetch_related('attach_set', 'tags__tag'))
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
            comments = Comment.objects.filter(article=self.object, is_active=True).select_related('user')
            kwargs['art_comments'] = self.paginate_qs(comments, 3)

        return super().get_context_data(**kwargs)
