from django import forms
from django.utils.translation import ugettext_lazy as _

from apps.articles.models import Comment, Article


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('article', 'parent', 'username', 'title', 'content')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.token = kwargs.pop('token', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        if not self.user and not self.token:
            raise forms.ValidationError(_('Не указан пользователь или токен'))
        return super().clean()

    def save(self, *args, **kwargs):
        if self.errors:
            return super().save(*args, **kwargs)

        if self.user:
            self.instance.user = self.user
        elif self.token:
            self.instance.token = self.token

        return super().save(*args, **kwargs)


class AddVideoForm(forms.ModelForm):
    video = forms.URLField(required=True)

    class Meta:
        model = Article
        fields = ('author_names', 'title', 'content', 'video')
