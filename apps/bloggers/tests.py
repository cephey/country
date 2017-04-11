from django.test import TestCase, Client
from apps.bloggers.factories import EntryFactory, BloggerFactory


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

        self.assertIn('Красный волк', resp.content.decode('utf-8'))
        self.assertIn('Черная лиса', resp.content.decode('utf-8'))
        self.assertIn('Белый петух', resp.content.decode('utf-8'))
        self.assertNotIn('Синие цыплята', resp.content.decode('utf-8'))
        self.assertNotIn('Желтый медведь', resp.content.decode('utf-8'))

    def test_blogger_entry_list_200(self):
        blogger = BloggerFactory()
        EntryFactory(blogger=blogger, description='Ниф-Ниф')
        EntryFactory(blogger=blogger, description='Наф-Наф')
        EntryFactory(blogger=blogger, description='Нуф-Нуф', is_active=False)

        resp = self.app.get('/bloggers/{}/'.format(blogger.id))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['blogger_obj'].id, blogger.id)

        self.assertIn('Ниф-Ниф', resp.content.decode('utf-8'))
        self.assertIn('Наф-Наф', resp.content.decode('utf-8'))
        self.assertNotIn('Нуф-Нуф', resp.content.decode('utf-8'))

    def test_blogger_entry_list_404(self):
        blogger = BloggerFactory(is_active=False)
        resp = self.app.get('/bloggers/{}/'.format(blogger.id))
        self.assertEqual(resp.status_code, 404)
