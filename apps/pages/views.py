from django.views.generic import TemplateView
from apps.utils.mixins.views import PageContextMixin


class AboutView(PageContextMixin, TemplateView):
    template_name = 'pages/about.html'
