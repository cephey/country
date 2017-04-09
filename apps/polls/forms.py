from django import forms
from django.contrib.contenttypes.models import ContentType

from apps.polls.models import Choice
from apps.votes.models import Vote


class ChoiceVoteForm(forms.Form):
    poll_id = forms.IntegerField()
    choices = forms.ChoiceField(choices=())

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.token = kwargs.pop('token', None)
        super().__init__(*args, **kwargs)
        try:
            poll_id = kwargs.get('data').get('poll_id')
        except AttributeError:
            pass
        else:
            self.fields['choices'] = forms.ChoiceField(
                choices=[(c.id, c.answer) for c in Choice.objects.filter(poll=poll_id)]
            )

    def save(self):
        params = {
            'object_id': int(self.cleaned_data['choices']),
            'content_type': ContentType.objects.get_for_model(Choice)
        }
        if self.user:
            params['user'] = self.user
        elif self.token:
            params['token'] = self.token
        else:
            raise Exception('User or Token no provided')
        params['defaults'] = {'score': 1}
        Vote.objects.get_or_create(**params)
