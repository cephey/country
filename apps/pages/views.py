from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from apps.utils.mixins.views import PageContextMixin, HeaderContextMixin
from apps.pages.models import ResourceType, Resource


class AboutView(PageContextMixin, TemplateView):
    template_name = 'pages/about.html'


class AdvertView(PageContextMixin, TemplateView):
    template_name = 'pages/advert.html'


class OppositionView(HeaderContextMixin, TemplateView):
    template_name = 'pages/opposition.html'

    def get_context_data(self, **kwargs):
        types = ResourceType.objects.active().order_by('id')

        parts = []
        for _type in types:
            parts.append({
                'type': _type,
                'resources': Resource.objects.active().filter(type=_type).order_by('-rating')[:5]
            })
        kwargs.update(
            parts=parts,
            new_resources=Resource.objects.active().order_by('-id')[:10]
        )
        kwargs.update(
            self.get_header_context()
        )
        return super().get_context_data(**kwargs)


class ResourceListView(HeaderContextMixin, TemplateView):
    template_name = 'pages/resource.html'
    _type = None

    def get(self, request, *args, **kwargs):
        self._type = get_object_or_404(ResourceType, pk=kwargs.get('pk'))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update(
            resource_type=self._type,
            resource_list=Resource.objects.active().filter(type=self._type).order_by('-rating')
        )
        kwargs.update(
            self.get_header_context()
        )
        return super().get_context_data(**kwargs)
