from django.conf.urls import url

from apps.articles import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^material/(?P<slug>[\w-]+)/$', views.SectionView.as_view(), name='section'),
    url(r'^material/(?P<slug>[\w-]+)/(?P<pk>\d+).html$', views.SectionView.as_view(), name='detail'),

    url(r'^export/rss.html', views.RssView.as_view(), name='rss')
]
