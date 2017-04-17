from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.views.generic import CreateView
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from apps.articles.models import Article, Comment
from apps.votes.forms import RatingForm, LikeForm


class BaseVoteCreateView(CreateView):
    model = None

    def get(self, request, *args, **kwargs):
        raise Http404

    def get_form_kwargs(self):
        kwargs = super(BaseVoteCreateView, self).get_form_kwargs()
        kwargs['content_type'] = ContentType.objects.get_for_model(self.model)

        if self.request.user.is_authenticated:
            kwargs['user'] = self.request.user
        else:
            kwargs['token'] = self.request.session.session_key

        return kwargs

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')

    def form_invalid(self, form):
        return HttpResponseRedirect(self.get_success_url())


class RatingView(BaseVoteCreateView):
    form_class = RatingForm
    model = Article

    def form_invalid(self, form):
        messages.info(self.request, _('Возможность оставить оценку временно недоступна'), extra_tags='article')
        return super().form_invalid(form)


class LikeView(BaseVoteCreateView):
    form_class = LikeForm
    model = Comment

    def form_invalid(self, form):
        comment_id = form.cleaned_data.get('object_id')
        if comment_id:
            messages.info(self.request, _('Возможность оценить комментарий временно недоступна'),
                          extra_tags='comment-{}'.format(comment_id))
        return super().form_invalid(form)
