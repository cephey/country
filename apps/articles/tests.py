from django.test import TestCase, Client

from apps.articles.factories import NoticeFactory
from apps.articles.models import Notice


class NoticeTestCase(TestCase):

    def setUp(self):
        self.app = Client()

    def test_notices_list_200(self):
        n1 = NoticeFactory(content='Воздух', status=Notice.STATUS.approved)
        NoticeFactory(content='Вода')
        n2 = NoticeFactory(content='Еда', status=Notice.STATUS.approved)

        resp = self.app.get('/notice/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['object_list']), 2)
        self.assertEqual(resp.context['object_list'][0].id, n2.id)
        self.assertEqual(resp.context['object_list'][1].id, n1.id)

        self.assertIn('Еда', resp.content.decode('utf-8'))
        self.assertIn('Воздух', resp.content.decode('utf-8'))
        self.assertNotIn('Вода', resp.content.decode('utf-8'))
