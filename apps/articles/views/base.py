from django.views.generic import ListView

from apps.articles.models import Article
from apps.utils.mixins.views import HeaderContextMixin, SidebarContextMixin


class BaseArticleListView(HeaderContextMixin, SidebarContextMixin, ListView):
    template_name = 'articles/list.html'
    paginate_by = 5
    model = Article
    page_kwarg = 'p'

    def get_context_data(self, **kwargs):
        kwargs.update(
            self.get_header_context()
        )
        kwargs.update(
            self.get_sidebar_context()
        )
        return super().get_context_data(**kwargs)
