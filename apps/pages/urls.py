from django.conf.urls import url

from apps.pages import views

urlpatterns = [
    url(r'^about/$', views.AboutView.as_view(), name='about'),
    url(r'^advert/$', views.AdvertView.as_view(), name='advert')
]
