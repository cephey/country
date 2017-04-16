from django import forms
from django.utils.translation import ugettext_lazy as _

from apps.articles.models import Article
from apps.votes.models import Vote


class VoteForm(forms.ModelForm):

    class Meta:
        model = Vote
        fields = ('object_id', 'score')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.token = kwargs.pop('token', None)
        self.content_type = kwargs.pop('content_type')
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.errors:
            return super().save(*args, **kwargs)

        data = dict(
            object_id=self.instance.object_id,
            content_type=self.content_type
        )
        if self.user:
            data['user'] = self.user.id
        elif self.token:
            data['token'] = self.token

        instance = Vote.objects.filter(**data).first()
        if instance:
            # If user has already voted, update score
            score = self.instance.score
            self.instance = instance
            self.instance.score = score
        else:
            self.instance.content_type = self.content_type
            if self.user:
                self.instance.user = self.user
            elif self.token:
                self.instance.token = self.token

        return super().save(*args, **kwargs)

    def clean(self):
        if not self.content_type:
            raise forms.ValidationError(_('Не указан тип объекта'))
        if not self.user and not self.token:
            raise forms.ValidationError(_('Не указан пользователь или токен'))
        return super().clean()


class RatingForm(VoteForm):

    def clean_object_id(self):
        object_id = self.cleaned_data['object_id']
        if not Article.objects.visible().filter(id=object_id).exists():
            raise forms.ValidationError(_('Указанной статьи не найдено'))
        return object_id

    def clean_score(self):
        score = self.cleaned_data['score']
        if score < 1 or score > 5:
            raise forms.ValidationError(_('Оценка должна быть от 1 до 5'))
        return score
