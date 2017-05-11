from django.contrib.auth.views import LoginView as DjangoLoginView

from apps.utils.mixins.views import PageContextMixin
from apps.users.forms import LoginForm


class LoginView(PageContextMixin, DjangoLoginView):
    template_name = 'users/login.html'
    form_class = LoginForm
    redirect_authenticated_user = True
