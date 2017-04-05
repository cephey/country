from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static

from apps.polls.views import PollDetailView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('apps.articles.urls', namespace='articles')),
    url(r'^author/', include('apps.authors.urls', namespace='authors')),
    url(r'^tags/', include('apps.tags.urls', namespace='tags')),

    url(r'^polls/', include('apps.polls.urls', namespace='polls')),
    url(r'^votes/blank.html', PollDetailView.as_view()),  # legacy
    # ?voteid=123 - id голосования
    # ?pvoteid=123&type=prev - при переходе с другого голосования (ссылка предыдущий)
    # ?pvoteid=123&type=next - при переходе с другого голосования (ссылка следующий)

    url(r'^votes/', include('apps.votes.urls', namespace='votes')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
