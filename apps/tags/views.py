from django.views.generic import TemplateView


class TagView(TemplateView):
    template_name = 'tags/detail.html'
