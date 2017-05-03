import uuid
import logging
import requests
import html2text
import xmltodict
import email.utils
from io import BytesIO
from urllib.parse import urljoin
from django.core.files import File

from forum.celery import app
from apps.bloggers.models import Blogger, Entry

logger = logging.getLogger(__name__)


@app.task(name='download_latest_blogger_entries')
def download_latest_blogger_entries(blogger_id):
    blogger = Blogger.objects.active().get(id=blogger_id)
    url = urljoin(blogger.link, Blogger.RSS_PATH)

    resp = requests.get(url)
    assert resp.status_code == 200

    data = xmltodict.parse(resp.content)
    info = data['rss']['channel']

    for item in info['item']:
        defaults = {
            'title': item.get('title'),
            'description': html2text.html2text(item.get('description') or ''),
        }
        if 'pubDate' in item:
            defaults['publish_date'] = email.utils.parsedate_to_datetime(item['pubDate'])

        entry, created = Entry.objects.get_or_create(link=item['link'], blogger_id=blogger_id, defaults=defaults)
        if created:
            logger.info('Create new entry for blogger %s: %s', blogger.id, entry.id)
        else:
            break  # entry already exist


@app.task(name='download_latest_entries')
def download_latest_entries():
    blogger_ids = Blogger.objects.active().values_list('id', flat=True)
    for blogger_id in blogger_ids:
        download_latest_blogger_entries.apply_async(args=(blogger_id,))


@app.task(name='update_single_blogger_photo')
def update_single_blogger_photo(blogger_id):
    blogger = Blogger.objects.active().get(id=blogger_id)
    url = urljoin(blogger.link, Blogger.RSS_PATH)

    resp = requests.get(url)
    assert resp.status_code == 200

    data = xmltodict.parse(resp.content)
    info = data['rss']['channel']

    resp = requests.get(info['image']['url'])
    blogger.photo.save(str(uuid.uuid4()), File(BytesIO(resp.content)), save=True)


@app.task(name='update_bloggers_photos')
def update_bloggers_photos():
    blogger_ids = Blogger.objects.active().values_list('id', flat=True)
    for blogger_id in blogger_ids:
        update_single_blogger_photo.apply_async(args=(blogger_id,))
