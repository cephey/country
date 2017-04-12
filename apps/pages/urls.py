from django.conf.urls import url

from apps.pages import views

urlpatterns = [
    url(r'^about/$', views.AboutView.as_view(), name='about'),
    url(r'^advert/$', views.AdvertView.as_view(), name='advert'),

    url(r'^opposition_hoop/$', views.OppositionView.as_view(), name='opposition'),
    url(r'^opposition_hoop/(?P<pk>\d+)/$', views.ResourceListView.as_view(), name='resource_list'),
]
