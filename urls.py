from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import views

from apps.articles.sitemaps import ArticleSitemap, SectionSitemap
from apps.polls.views import PollDetailView
from apps.tags.sitemaps import TagSitemap


urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^pda/', include('apps.pda.urls', namespace='pda')),

    url(r'', include('apps.articles.urls', namespace='articles')),
    url(r'', include('apps.pages.urls', namespace='pages')),
    url(r'', include('apps.forum.urls', namespace='forum')),
    url(r'', include('apps.users.urls', namespace='users')),
    url(r'^bloggers/', include('apps.bloggers.urls', namespace='bloggers')),
    url(r'^author/', include('apps.authors.urls', namespace='authors')),
    url(r'^tags/', include('apps.tags.urls', namespace='tags')),

    # polls
    url(r'^polls/', include('apps.polls.urls', namespace='polls')),
    url(r'^votes/blank.html', PollDetailView.as_view()),  # deprecated

    url(r'^votes/', include('apps.votes.urls', namespace='votes')),

    # captcha
    url(r'^captcha/', include('captcha.urls'))

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# sitemaps
sitemaps = {
    'news': ArticleSitemap,
    'sections': SectionSitemap,
    'tags': TagSitemap
}
urlpatterns = [
    url(r'^sitemap\.xml$', views.index, {'sitemaps': sitemaps}),
    url(r'^sitemap-(?P<section>.+)\.xml$', views.sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap')
] + urlpatterns


# debug_toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
