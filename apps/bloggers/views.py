from django.views.generic import ListView
from django.shortcuts import get_object_or_404

from apps.utils.mixins.views import PageContextMixin
from apps.bloggers.models import Entry, Blogger


class BaseEntryListView(PageContextMixin, ListView):
    paginate_by = 6
    page_kwarg = 'p'
    model = Entry
    ordering = ('-publish_date',)

    def get_queryset(self):
        return super().get_queryset().active().select_related('blogger')


class LastEntryListView(BaseEntryListView):
    template_name = 'bloggers/last_list.html'

    def get_context_data(self, **kwargs):
        kwargs['blogger_list'] = Blogger.objects.active()[:12]
        return super().get_context_data(**kwargs)


class BloggerEntryListView(BaseEntryListView):
    template_name = 'bloggers/blogger_list.html'
    blogger = None

    def get(self, request, *args, **kwargs):
        if 'pk' in kwargs:
            params = {'id': kwargs['pk']}
        elif 'legacy_pk' in kwargs:
            params = {'ext_id': kwargs['legacy_pk']}

        self.blogger = get_object_or_404(Blogger.objects.active(), **params)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(blogger=self.blogger)

    def get_context_data(self, **kwargs):
        kwargs['blogger_obj'] = self.blogger
        return super().get_context_data(**kwargs)
