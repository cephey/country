from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.views.generic import FormView, CreateView
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from apps.articles.models import Article
from apps.votes.forms import RatingForm


class RatingView(CreateView):
    form_class = RatingForm

    def get(self, request, *args, **kwargs):
        raise Http404

    def get_form_kwargs(self):
        kwargs = super(RatingView, self).get_form_kwargs()
        kwargs['content_type'] = ContentType.objects.get_for_model(Article)

        if self.request.user.is_authenticated:
            kwargs['user'] = self.request.user
        else:
            kwargs['token'] = self.request.session.session_key

        return kwargs

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')

    def form_invalid(self, form):
        messages.info(self.request, _('Возможность оставить оценку временно недоступна'))
        return HttpResponseRedirect(self.get_success_url())


class LikeView(FormView):
    pass
