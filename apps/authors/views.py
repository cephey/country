from django.views.generic import DetailView

from apps.utils.mixins.views import PageContextMixin
from apps.articles.models import Article
from apps.authors.models import Author


class AuthorDetailView(PageContextMixin, DetailView):
    template_name = 'authors/detail.html'
    model = Author

    def get_context_data(self, **kwargs):
        kwargs['obj_atricles'] = (Article.objects.visible()
                                  .select_related('section')
                                  .filter(authors=self.object)
                                  .order_by('-id')[:10])
        return super().get_context_data(**kwargs)
