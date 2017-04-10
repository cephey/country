from django.test import TestCase, Client


class PagesTestCase(TestCase):

    def setUp(self):
        self.app = Client()

    def test_about_page_200(self):
        resp = self.app.get('/about/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Свободы хотим, демократии и прогресса', resp.content.decode('utf-8'))
