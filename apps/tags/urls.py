from django.conf.urls import url

from apps.tags import views

urlpatterns = [
    url(r'^(?P<pk>\d+)/$', views.TagView.as_view(), name='detail')
]
