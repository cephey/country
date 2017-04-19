from datetime import timedelta

from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.http import Http404, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.views.generic import TemplateView, ListView, DetailView, RedirectView, CreateView

from apps.articles.models import (Article, Section, Comment, Notice, BEST, NEWS, VIDEO,
                                  NAVIGATE_SECTIONS, VIDEO_SECTIONS, GENERIC_SECTIONS)
from apps.articles.forms import CommentForm
from apps.utils.mixins.views import PageContextMixin
from apps.utils.mixins.paginator import PaginatorMixin
from apps.utils.mixins.access import StaffRequiredMixin


class IndexView(PageContextMixin, TemplateView):
    template_name = 'articles/index.html'

    def get_context_data(self, **kwargs):
        sections = Section.objects.filter(slug__in=NAVIGATE_SECTIONS)

        materials = {}
        for section in sections:
            materials[section.slug] = {
                'section': section,
                'articles': Article.objects.visible().filter(section=section)[:6]
            }

        kwargs.update(
            main_news=(Article.objects.visible()
                       .filter(is_news=True)
                       .order_by('-publish_date')
                       .first()),
            main_material=(Article.objects.visible()
                           .filter(is_news=False)
                           .order_by('-publish_date', '-comments_count')
                           .first()),
            materials=materials
        )
        return super().get_context_data(**kwargs)


class BaseArticleListView(PageContextMixin, ListView):
    template_name = 'articles/list.html'
    paginate_by = 5
    queryset = Article.objects.visible().select_related('section')
    page_kwarg = 'p'
    ordering = '-id'


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


class ArticleDetailView(PageContextMixin, PaginatorMixin, DetailView):
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
        kwargs['art_section'] = self.section or self.object.section

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


class CreateArticleView(PageContextMixin, CreateView):
    template_name = 'articles/create.html'
    model = Article
    fields = ('title', 'description', 'content', 'author_names')

    def get_success_url(self):
        return reverse('articles:create') + '#res'

    def form_valid(self, form):
        messages.info(self.request, _('Материал успешно добавлен. '
                                      'После одобрения редактора он появится на сайте.'))
        return super().form_valid(form)


class NoticeListView(PageContextMixin, CreateView):
    template_name = 'articles/notice_list.html'
    model = Notice
    fields = ('content',)

    def get_success_url(self):
        return reverse('articles:notice') + '#send'

    def form_valid(self, form):
        messages.info(self.request, _('Ваше объявление будет обязательно рассмотрено '
                                      'нашим редактором в самое ближайшее время.'))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['object_list'] = Notice.objects.filter(status=Notice.STATUS.approved)[:20]
        return super().get_context_data(**kwargs)


class VideoContextMixin(object):

    def get_context_data(self, **kwargs):
        sections = Section.objects.filter(slug__in=VIDEO_SECTIONS, is_video=True)

        materials = {}
        for section in sections:
            if section.slug in ('video_fpolitic', 'video_national'):
                n = 5
            elif section.slug.startswith('video_partner'):
                n = 2
            else:
                n = 3
            materials[section.slug] = {
                'section': section,
                'articles': Article.objects.visible().filter(section=section)[:n]
            }
        kwargs['materials'] = materials
        return super().get_context_data(**kwargs)


class VideoIndexView(VideoContextMixin, PageContextMixin, TemplateView):
    template_name = 'articles/video.html'

    def get(self, request, *args, **kwargs):
        # handle deprecated url
        if request.GET.get('video'):
            try:
                video_id = int(request.GET['video'])
            except (TypeError, ValueError):
                pass
            else:
                url = reverse('articles:video_detail', kwargs={'pk': video_id})
                return HttpResponsePermanentRedirect(url)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update(
            main_news=(Article.objects.visible()
                       .filter(is_news=True, section__is_video=True)
                       .order_by('-publish_date')
                       .first()),
            main_material=(Article.objects.visible()
                           .filter(is_news=False, section__is_video=True)
                           .order_by('-publish_date', '-comments_count')
                           .first())
        )
        return super().get_context_data(**kwargs)


class VideoDetailView(VideoContextMixin, PageContextMixin, DetailView):
    template_name = 'articles/video.html'
    queryset = Article.objects.visible().select_related('section')

    def get_context_data(self, **kwargs):
        kwargs['main_news'] = self.object
        return super().get_context_data(**kwargs)


class ActionView(StaffRequiredMixin, RedirectView):

    def get(self, request, *args, **kwargs):
        (Article.objects.visible()
         .filter(pk=kwargs.get('pk'))
         .update(discussion_status=kwargs.get('action')))
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return self.request.META.get('HTTP_REFERER')


class CommentCreateView(PageContextMixin, CreateView):
    template_name = 'articles/create_comment.html'

    form_class = CommentForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        if self.request.user.is_authenticated:
            kwargs['user'] = self.request.user
        else:
            kwargs['token'] = self.request.session.session_key

        return kwargs

    def get_success_url(self):
        if self.object:
            return self.object.article.get_absolute_url()
        return self.request.META.get('HTTP_REFERER')


class CommentDeleteView(StaffRequiredMixin, RedirectView):

    def get(self, request, *args, **kwargs):
        comment = Comment.objects.filter(pk=kwargs.get('pk')).first()
        if comment:
            comment.is_active = False
            comment.save(update_fields=['is_active'])
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return self.request.META.get('HTTP_REFERER')


class RssView(TemplateView):
    template_name = 'articles/rss.html'
