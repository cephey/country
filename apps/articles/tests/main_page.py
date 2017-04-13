from django.test import TestCase, Client


class MainPageTestCase(TestCase):

    def setUp(self):
        self.app = Client()

    def test_200_ok(self):
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Главная новость', resp.content.decode('utf-8'))
        self.assertIn('Материал дня', resp.content.decode('utf-8'))
