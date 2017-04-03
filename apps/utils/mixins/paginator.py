from django.http import Http404
from django.core.paginator import InvalidPage, Paginator


class PaginatorMixin(object):
    page_kwarg = 'pf'

    def paginate_qs(self, qs, page_size):
        paginator = Paginator(qs, page_size)
        page = self.request.GET.get(self.page_kwarg) or 1
        try:
            page_number = int(page)
        except ValueError:
            raise Http404
        try:
            return paginator.page(page_number)
        except InvalidPage:
            raise Http404
