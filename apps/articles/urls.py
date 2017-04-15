from django.conf.urls import url

from apps.articles import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),

    # articles
    url(r'^material/(?P<slug>[\w-]+)/(?P<pk>\d+).html', views.ArticleDetailView.as_view()),  # deprecated
    url(r'^material/(?P<slug>[\w-]+)/(?P<pk>\d+)/$', views.ArticleDetailView.as_view(), name='detail'),

    # sections
    url(r'^material/(?P<slug>[\w-]+).html', views.SectionView.as_view()),  # deprecated
    url(r'^material/(?P<slug>[\w-]+)/$', views.SectionView.as_view(), name='section'),

    # video
    url(r'^video/$', views.VideoIndexView.as_view(), name='video'),
    # /video/?video=123 - article detail

    url(r'^addnews/$', views.CreateArticleView.as_view(), name='create'),

    url(r'^material/(?P<pk>\d+)/(?P<action>(open|close))/$', views.ActionView.as_view(), name='action'),

    url(r'^notice/$', views.NoticeListView.as_view(), name='notice'),

    url(r'^export/rss.html', views.RssView.as_view(), name='rss')
]
