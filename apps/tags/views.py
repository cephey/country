from django.shortcuts import get_object_or_404

from apps.articles.views import BaseArticleListView
from apps.tags.models import Tag


class TagView(BaseArticleListView):
    tag = None

    def get(self, request, *args, **kwargs):
        self.tag = get_object_or_404(Tag, pk=kwargs.get('pk'))
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(tags__tag=self.tag)

    def get_context_data(self, **kwargs):
        kwargs['partition'] = self.tag
        return super().get_context_data(**kwargs)
