from django.conf.urls import url

from apps.authors import views

urlpatterns = [
    url(r'^(?P<pk>\d+)', views.AuthorDetailView.as_view(), name='detail'),
]
