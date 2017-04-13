from django.test import TestCase, Client

from apps.articles.factories import NoticeFactory
from apps.articles.models import Notice


class NoticeTestCase(TestCase):

    def setUp(self):
        self.app = Client()

    def test_notices_list_200(self):
        n1 = NoticeFactory(content='Воздух')
        NoticeFactory(content='Вода', status=Notice.STATUS.new)
        n2 = NoticeFactory(content='Еда')

        resp = self.app.get('/notice/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['object_list']), 2)
        self.assertEqual(resp.context['object_list'][0].id, n2.id)
        self.assertEqual(resp.context['object_list'][1].id, n1.id)

        self.assertIn('Еда', resp.content.decode('utf-8'))
        self.assertIn('Воздух', resp.content.decode('utf-8'))
        self.assertNotIn('Вода', resp.content.decode('utf-8'))

    def test_create_ok(self):
        data = {
            'content': 'Бравые военные'
        }
        resp = self.app.post('/notice/', data, follow=True)
        url, status_code = resp.redirect_chain[0]
        self.assertEqual(status_code, 302)
        self.assertEqual(url, '/notice/#send')
        self.assertIn('Ваше объявление будет обязательно рассмотрено нашим редактором',
                      resp.content.decode('utf-8'))

        notices = Notice.objects.all()
        self.assertEqual(len(notices), 1)
        self.assertEqual(notices[0].content, 'Бравые военные')
        self.assertEqual(notices[0].status, Notice.STATUS.new)

    def test_create_fail(self):
        data = {
            'content': 'Ы' * 250
        }
        resp = self.app.post('/notice/', data)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Убедитесь, что это значение содержит не более 200 символов (сейчас 250)',
                      resp.content.decode('utf-8'))
        self.assertFalse(Notice.objects.exists())
