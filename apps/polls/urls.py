from django.conf.urls import url

from apps.polls import views

urlpatterns = [
    url(r'^$', views.ChoiceVoteView.as_view(), name='choice_vote'),
    url(r'^(?P<pk>\d+)/$', views.PollDetailView.as_view(), name='detail')
]
