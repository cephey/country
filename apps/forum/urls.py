from django.conf.urls import url

from apps.forum import views

urlpatterns = [
    url(r'^dialog/$', views.ForumIndexView.as_view()),  # deprecated
    url(r'^forum/$', views.ForumIndexView.as_view(), name='index'),

    url(r'^forum/(?P<pk>\d+)/$', views.ForumThreadView.as_view(), name='thread')
]
