import logging
import requests
import xmltodict
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from forum.celery import app
from apps.articles.models import Article, Section

logger = logging.getLogger(__name__)


@app.task(name='download_latest_section_partner_videos')
def download_latest_section_partner_videos(section_id):
    section = Section.objects.active().get(id=section_id)

    resp = requests.get(section.rss_link)
    assert resp.status_code == 200

    data = xmltodict.parse(resp.content)
    info = data['feed']

    for entry in info['entry']:
        defaults = {
            'title': entry.get('title'),
            'status': Article.STATUS.approved
        }
        if 'published' in entry:
            defaults['publish_date'] = parse_datetime(entry['published'])
        else:
            defaults['publish_date'] = timezone.now()

        article, created = (Article.objects
                            .get_or_create(video=entry['link']['@href'],
                                           section_id=section_id, defaults=defaults))
        if created:
            logger.info('Create new article for section %s: %s', section.id, article.id)
        else:
            break  # article already exist


@app.task(name='download_latest_partners_videos')
def download_latest_partners_videos():
    section_ids = (Section.objects.active()
                   .filter(~Q(channel=''), is_video=True)
                   .values_list('id', flat=True))
    for section_id in section_ids:
        download_latest_section_partner_videos.apply_async(args=(section_id,))
