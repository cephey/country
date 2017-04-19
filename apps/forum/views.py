from datetime import timedelta

from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponsePermanentRedirect
from django.views.generic import TemplateView, ListView, DetailView, RedirectView, CreateView

from apps.articles.models import (Article, Section, Comment, Notice, BEST, NEWS, VIDEO,
                                  NAVIGATE_SECTIONS, VIDEO_SECTIONS, GENERIC_SECTIONS)
from apps.articles.forms import CommentForm
from apps.utils.mixins.views import PageContextMixin, HeaderContextMixin
from apps.utils.mixins.paginator import PaginatorMixin
from apps.utils.mixins.access import StaffRequiredMixin


class BaseForumListView(HeaderContextMixin, ListView):

    def get_context_data(self, **kwargs):
        kwargs.update(
            self.get_header_context()
        )
        return super().get_context_data(**kwargs)


class ForumIndexView(BaseForumListView):
    template_name = 'forum/index.html'
    paginate_by = 10
    queryset = Article.objects.open().prefetch_related('authors')
    page_kwarg = 'p'
    ordering = '-id'


class ForumThreadView(BaseForumListView):
    template_name = 'forum/thread.html'
    paginate_by = 3
    queryset = Comment.objects.active()
    page_kwarg = 'p'
    ordering = '-id'
