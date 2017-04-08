from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.views.generic import DetailView, FormView

from apps.utils.mixins.views import PageContextMixin
from apps.polls.models import Poll
from apps.polls.forms import ChoiceVoteForm


class PollDetailView(PageContextMixin, DetailView):
    template_name = 'polls/detail.html'
    model = Poll

    def get_queryset(self):
        return super().get_queryset().prefetch_related('choice_set')

    def get_context_data(self, **kwargs):
        kwargs.update(
            prev_poll=Poll.objects.filter(id__lt=self.object.id).first(),
            next_poll=Poll.objects.filter(id__gt=self.object.id).last()
        )
        return super().get_context_data(**kwargs)


class ChoiceVoteView(FormView):
    form_class = ChoiceVoteForm
    poll_id = None

    def get(self, request, *args, **kwargs):
        raise Http404

    def get_success_url(self):
        if self.poll_id:
            return reverse('polls:detail', kwargs={'pk': self.poll_id})
        return self.request.META.get('HTTP_REFERER')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.is_authenticated:
            kwargs['user'] = self.request.user
        else:
            kwargs['token'] = self.request.session.session_key
        return kwargs

    def form_valid(self, form):
        self.poll_id = form.cleaned_data['poll_id']
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        self.poll_id = form.cleaned_data.get('poll_id')
        return HttpResponseRedirect(self.get_success_url())
