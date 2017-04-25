from django.conf.urls import url

from apps.pda import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),

    # articles
    url(r'^material/(?P<slug>[\w-]+)/(?P<pk>\d+).html', views.ArticleDetailView.as_view()),  # deprecated
    url(r'^material/(?P<slug>[\w-]+)/(?P<pk>\d+)/$', views.ArticleDetailView.as_view(), name='detail'),

    # sections
    url(r'^material/(?P<slug>[\w-]+).html', views.SectionView.as_view()),  # deprecated
    url(r'^material/(?P<slug>[\w-]+)/$', views.SectionView.as_view(), name='section')
]
