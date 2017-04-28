from django.urls import reverse
from django.http import Http404, HttpResponseRedirect
from django.views.generic import DetailView, FormView

from apps.utils.mixins.views import PageContextMixin
from apps.polls.models import Poll
from apps.polls.forms import ChoiceVoteForm


class PollDetailView(PageContextMixin, DetailView):
    template_name = 'polls/detail.html'
    queryset = Poll.objects.active().prefetch_related('choice_set')

    def get_object(self, queryset=None):
        queryset = self.get_queryset()

        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk:
            queryset = queryset.filter(pk=pk)
        else:
            # Support deprecated urls:
            queryset = self.queryset_by_query_params(queryset)

        try:
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        kwargs.update(
            prev_poll=Poll.objects.active().filter(id__lt=self.object.id).order_by('-pk').first(),
            next_poll=Poll.objects.active().filter(id__gt=self.object.id).order_by('-pk').last()
        )
        return super().get_context_data(**kwargs)

    def queryset_by_query_params(self, queryset):
        """
        Support deprecated urls:
            ?voteid=123
            ?pvoteid=123&type=prev
            ?pvoteid=123&type=next
        looking up by query params
        """
        voteid = self.request.GET.get('voteid')
        if voteid:
            try:
                queryset = queryset.filter(pk=int(voteid))
            except (TypeError, ValueError):
                raise Http404

        pvoteid = self.request.GET.get('pvoteid')
        if pvoteid:
            try:
                pvoteid = int(pvoteid)
            except (TypeError, ValueError):
                raise Http404
            else:
                _type = self.request.GET.get('type')
                if _type == 'next':
                    next_obj = Poll.objects.active().filter(id__gt=pvoteid).order_by('-pk').only('id').last()
                    if not next_obj:
                        raise Http404
                    pvoteid = next_obj.id
                elif _type == 'prev':
                    prev_obj = Poll.objects.active().filter(id__lt=pvoteid).order_by('-pk').only('id').first()
                    if not prev_obj:
                        raise Http404
                    pvoteid = prev_obj.id
                queryset = queryset.filter(pk=pvoteid)

        if not voteid and not pvoteid:
            raise Http404

        return queryset


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
