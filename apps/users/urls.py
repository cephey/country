from django.conf.urls import url
from django.contrib.auth.views import LogoutView

from apps.users import views

urlpatterns = [
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
]
