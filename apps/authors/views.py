from django.views.generic import TemplateView


class AuthorView(TemplateView):
    template_name = 'authors/detail.html'
