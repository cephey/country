"""apps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('apps.articles.urls', namespace='articles')),
    url(r'^author/', include('apps.authors.urls', namespace='authors')),
    url(r'^polls/', include('apps.polls.urls', namespace='polls')),
    url(r'^tags/', include('apps.tags.urls', namespace='tags')),
    url(r'^votes/', include('apps.votes.urls', namespace='votes')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
