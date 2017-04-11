from django.conf.urls import url

from apps.bloggers import views

urlpatterns = [
    url(r'^$', views.LastEntryListView.as_view(), name='last_entry_list'),

    url(r'^(?P<pk>\d+).html', views.BloggerEntryListView.as_view()),  # deprecated
    url(r'^(?P<pk>\d+)/$', views.BloggerEntryListView.as_view(), name='blogger_entry_list')
]
