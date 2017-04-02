from django.conf.urls import url

from apps.votes import views

urlpatterns = [
    url(r'^article/$', views.RatingView.as_view(), name='article'),
    url(r'^comment/$', views.LikeView.as_view(), name='comment'),
]
