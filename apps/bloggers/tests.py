import os
import pytz
import responses
from datetime import datetime

from django.conf import settings
from django.test import TestCase, Client
from django.core.management import call_command

from apps.bloggers.factories import EntryFactory, BloggerFactory
from apps.bloggers.tasks import download_latest_entries, update_bloggers_photos
from apps.bloggers.models import Blogger, Entry


class EntryTestCase(TestCase):

    def setUp(self):
        self.app = Client()

    def test_last_entry_list_200(self):
        blogger1 = BloggerFactory()
        blogger2 = BloggerFactory()
        blogger3 = BloggerFactory(is_active=False)

        EntryFactory(blogger=blogger1, description='Красный волк')
        EntryFactory(blogger=blogger1, description='Черная лиса')
        EntryFactory(blogger=blogger2, description='Белый петух')
        EntryFactory(blogger=blogger2, description='Синие цыплята', is_active=False)
        EntryFactory(blogger=blogger3, description='Желтый медведь')

        resp = self.app.get('/bloggers/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['blogger_list'][0].id, blogger2.id)
        self.assertEqual(resp.context['blogger_list'][1].id, blogger1.id)

        self.assertContains(resp, 'Красный волк')
        self.assertContains(resp, 'Черная лиса')
        self.assertContains(resp, 'Белый петух')
        self.assertNotContains(resp, 'Синие цыплята')
        self.assertNotContains(resp, 'Желтый медведь')

    def test_blogger_entry_list_200(self):
        blogger = BloggerFactory()
        EntryFactory(blogger=blogger, description='Ниф-Ниф')
        EntryFactory(blogger=blogger, description='Наф-Наф')
        EntryFactory(blogger=blogger, description='Нуф-Нуф', is_active=False)

        resp = self.app.get('/bloggers/{}/'.format(blogger.id))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['blogger_obj'].id, blogger.id)

        self.assertContains(resp, 'Ниф-Ниф')
        self.assertContains(resp, 'Наф-Наф')
        self.assertNotContains(resp, 'Нуф-Нуф')

    def test_blogger_entry_list_404(self):
        blogger = BloggerFactory(is_active=False)
        resp = self.app.get('/bloggers/{}/'.format(blogger.id))
        self.assertEqual(resp.status_code, 404)

    def test_deprecated_url(self):
        blogger = BloggerFactory(ext_id=454540)
        resp = self.app.get('/bloggers/454540.html')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['blogger_obj'].id, blogger.id)


class TaskTestCase(TestCase):

    @responses.activate
    def test_download_latest_entries(self):
        responses.add(responses.GET, 'http://anna.country.com/data/rss/',
                      body=open('fixtures/xml/blogger_rss.xml').read())

        blogger = BloggerFactory(link='http://anna.country.com')
        download_latest_entries()

        entries = Entry.objects.order_by('id')
        self.assertEqual(len(entries), 2)

        self.assertEqual(entries[0].blogger, blogger)
        self.assertEqual(entries[0].title, 'Национальная валюта')
        self.assertEqual(entries[0].link, 'http://anna.country.com/260976.html')
        self.assertEqual(entries[0].publish_date, datetime(2017, 5, 3, 4, 5, 30, tzinfo=pytz.utc))
        self.assertTrue(entries[0].description.startswith('Сказать же публично правду о том, чем на самом деле'))

        self.assertEqual(entries[1].blogger, blogger)
        self.assertEqual(entries[1].title, 'Это круто!')
        self.assertEqual(entries[1].link, 'http://anna.country.com/260710.html')
        self.assertEqual(entries[1].publish_date, datetime(2017, 5, 2, 3, 43, 48, tzinfo=pytz.utc))
        self.assertIn('Первое\n\nи основное', entries[1].description)

    @responses.activate
    def test_download_blogger_photo(self):
        responses.add(responses.GET, 'http://anna.country.com/data/rss/',
                      body=open('fixtures/xml/blogger_rss.xml').read())
        responses.add(responses.GET, 'http://anna.country.com/12345678/87654321',
                      body=open('fixtures/i/flag.jpg', 'rb').read())

        blogger = BloggerFactory(link='http://anna.country.com', photo=None)
        update_bloggers_photos()

        blogger.refresh_from_db()
        self.assertTrue(blogger.photo)
        self.assertIn('bloggers/', blogger.photo.name)


class ImportTestCase(TestCase):

    def test_import_bloggers(self):
        call_command(
            'migrate_bloggers',
            path=os.path.join(settings.BASE_DIR, 'fixtures/csv/forum_bloggers.csv')
        )
        bloggers = Blogger.objects.order_by('id')
        self.assertEqual(len(bloggers), 5)

        self.assertEqual(bloggers[0].first_name, 'Дарья')
        self.assertEqual(bloggers[0].last_name, 'Митина')
        self.assertEqual(bloggers[0].link, 'http://kolobok1973.livejournal.com/')
        self.assertTrue(bloggers[0].is_active)
        self.assertEqual(bloggers[0].ext_id, 2373877)

        self.assertEqual(bloggers[1].first_name, 'Илья')
        self.assertFalse(bloggers[2].is_active)
        self.assertEqual(bloggers[3].link, 'http://m-kalashnikov.livejournal.com/')
        self.assertEqual(bloggers[4].ext_id, 2373893)

    def test_import_entries(self):
        blogger1 = BloggerFactory(ext_id=11299)
        blogger2 = BloggerFactory(ext_id=14500)
        call_command(
            'migrate_entries',
            path=os.path.join(settings.BASE_DIR, 'fixtures/csv/forum_bloggers_news.csv')
        )
        entries = Entry.objects.order_by('id')
        self.assertEqual(len(entries), 4)

        self.assertEqual(entries[0].title, 'К киприотам России')
        self.assertTrue(entries[0].description.startswith('итак, г-н Медведев сообщил, что на Кипре заблокированы '
                                                          'деньги российских\nгосударственных структур.'))
        self.assertEqual(entries[0].blogger, blogger2)
        self.assertEqual(entries[0].link, 'http://denis-bilunov.livejournal.com/193383.html')
        self.assertEqual(entries[0].publish_date, datetime(2013, 3, 21, 7, 50, 35, tzinfo=pytz.utc))

        self.assertEqual(entries[1].title, 'Жанаозен: неизвестная трагедия')
        self.assertEqual(entries[1].blogger, blogger2)

        self.assertEqual(entries[2].description, 'Так так )))\n\n')
        self.assertEqual(entries[2].blogger, blogger1)

        self.assertEqual(entries[3].blogger, blogger1)
        self.assertEqual(entries[3].publish_date, datetime(2014, 4, 11, 9, 48, 39, tzinfo=pytz.utc))

