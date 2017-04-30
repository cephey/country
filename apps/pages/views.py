from django.urls import reverse
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.http import HttpResponsePermanentRedirect

from apps.utils.mixins.views import PageContextMixin, HeaderContextMixin
from apps.pages.models import Partition, Resource
from apps.pages.jobs import IndexOppositionPartitionResourcesJob


class AboutView(PageContextMixin, TemplateView):
    template_name = 'pages/about.html'


class AdvertView(PageContextMixin, TemplateView):
    template_name = 'pages/advert.html'


class BaseOppositionView(HeaderContextMixin, TemplateView):

    def get_context_data(self, **kwargs):
        kwargs.update(
            self.get_header_context()
        )
        return super().get_context_data(**kwargs)


class OppositionView(BaseOppositionView):
    template_name = 'pages/opposition/index.html'

    def get(self, request, *args, **kwargs):
        # handle deprecated url
        if request.GET.get('part'):
            try:
                part_id = int(request.GET['part'])
            except (TypeError, ValueError):
                pass
            else:
                return HttpResponsePermanentRedirect(reverse('pages:partition', kwargs={'pk': part_id}))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update(
            partitions=IndexOppositionPartitionResourcesJob().get(),
            new_resources=Resource.objects.active().order_by('-id')[:10]
        )
        return super().get_context_data(**kwargs)


class PartitionView(BaseOppositionView):
    template_name = 'pages/opposition/partition.html'
    partition = None

    def get(self, request, *args, **kwargs):
        self.partition = get_object_or_404(Partition, pk=kwargs.get('pk'), is_active=True)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update(
            partition=self.partition,
            resource_list=Resource.objects.active().filter(partition=self.partition).order_by('-rating')
        )
        return super().get_context_data(**kwargs)
