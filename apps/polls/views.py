from django.views.generic import TemplateView


class PollView(TemplateView):
    template_name = 'polls/detail.html'
