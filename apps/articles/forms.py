from django import forms
from django.utils.translation import ugettext_lazy as _
from captcha.fields import CaptchaField
from ckeditor.fields import RichTextFormField

from apps.articles.models import Comment, Article


class CommentForm(forms.ModelForm):
    captcha = CaptchaField()

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


class CreateArticleForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea, required=True)
    captcha = CaptchaField()

    class Meta:
        model = Article
        fields = ('title', 'description', 'content', 'author_names')


class AddVideoForm(forms.ModelForm):
    video = forms.URLField(required=True)
    captcha = CaptchaField()

    class Meta:
        model = Article
        fields = ('author_names', 'title', 'content', 'video')


class AdminArticleForm(forms.ModelForm):
    content = RichTextFormField(label=Article._meta.get_field('content').verbose_name)

    class Meta:
        model = Article
        fields = '__all__'
        widgets = {
            'status': forms.RadioSelect,
            'discussion_status': forms.RadioSelect
        }


class AdminNoticeForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = '__all__'
        widgets = {
            'content': forms.Textarea(attrs={'cols': 80, 'rows': 8}),
            'status': forms.RadioSelect
        }
