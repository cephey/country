from django.test import TestCase, Client

from apps.users.factories import UserFactory


class AuthTestCase(TestCase):

    def setUp(self):
        self.app = Client()

    def test_login_page_200(self):
        resp = self.app.get('/login/')
        self.assertEqual(resp.status_code, 200)

        self.assertContains(resp, 'Вход')
        self.assertContains(resp, 'Логин')
        self.assertContains(resp, 'Пароль')

    def test_redirect_auth_user(self):
        user = UserFactory(username='andrey')
        user.set_password('secret')
        user.save()
        self.app.login(username='andrey', password='secret')

        resp = self.app.get('/login/')
        self.assertEqual(resp.status_code, 302)

    def test_login(self):
        user = UserFactory(username='andrey')
        user.set_password('secret')
        user.save()

        data = {
            'username': 'andrey',
            'password': 'secret',
            'captcha_0': '*',
            'captcha_1': 'passed'
        }
        resp = self.app.post('/login/?next=/forum/', data)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/forum/')

    def test_login_fail(self):
        user = UserFactory(username='andrey')
        user.set_password('secret')
        user.save()

        data = {
            'username': 'andrey',
            'password': 'wrong',
            'captcha_0': '*',
            'captcha_1': 'passed'
        }
        resp = self.app.post('/login/', data)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('введите правильные имя пользователя и пароль', resp.context['form'].errors['__all__'][0])
        self.assertContains(resp, 'введите правильные имя пользователя и пароль')

        data = {
            'password': 'secret',
            'captcha_0': '*',
            'captcha_1': 'passed'
        }
        resp = self.app.post('/login/', data)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Обязательное поле')

    def test_logout(self):
        user = UserFactory(username='andrey')
        user.set_password('secret')
        user.save()
        self.app.login(username='andrey', password='secret')

        resp = self.app.get('/logout/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/login/')
