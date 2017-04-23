from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from apps.articles.models import Article, Comment
from apps.articles.forms import CommentForm
from apps.utils.mixins.views import PageContextMixin, HeaderContextMixin


class ForumIndexView(HeaderContextMixin, ListView):
    template_name = 'forum/index.html'
    paginate_by = 10
    queryset = Article.objects.open().prefetch_related('authors')
    page_kwarg = 'p'
    ordering = '-id'

    def get_context_data(self, **kwargs):
        kwargs.update(
            self.get_header_context()
        )
        return super().get_context_data(**kwargs)


class ForumThreadView(PageContextMixin, ListView):
    template_name = 'forum/thread.html'
    paginate_by = 3
    queryset = Comment.objects.active()
    article = None
    page_kwarg = 'p'
    ordering = 'id'

    def get(self, request, *args, **kwargs):
        self.article = get_object_or_404(Article.objects.open(), pk=kwargs.get('pk'))
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        self.queryset = self.queryset.filter(article=self.article)
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        kwargs.update(
            thread=self.article,
            comment_form=CommentForm()
        )
        return super().get_context_data(**kwargs)
