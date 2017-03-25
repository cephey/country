from django.conf.urls import url

from apps.polls import views

urlpatterns = [
    url(r'^(?P<pk>\d+)/$', views.PollView.as_view(), name='detail')
]
