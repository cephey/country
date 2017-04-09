from django.test import TestCase, Client
from apps.polls.factories import PollFactory, ChoiceFactory


class PollTestCase(TestCase):

    def setUp(self):
        self.app = Client()

    def test_detail_page(self):
        poll = PollFactory(question='Как так?', sum_votes=10)
        for answer, vote_count in (('первый', 2), ('второй', 3), ('третий', 5)):
            ChoiceFactory(poll=poll, answer=answer, vote_count=vote_count)

        resp = self.app.get('/polls/{}/'.format(poll.id))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Результаты голосования', resp.content.decode('utf-8'))
        self.assertIn('Как так?', resp.content.decode('utf-8'))

        self.assertIn('font-size:90%;width:20%;background-color:#990000', resp.content.decode('utf-8'))
        self.assertIn('первый (2)', resp.content.decode('utf-8'))

        self.assertIn('font-size:90%;width:30%;background-color:#990000', resp.content.decode('utf-8'))
        self.assertIn('второй (3)', resp.content.decode('utf-8'))

        self.assertIn('font-size:90%;width:50%;background-color:#990000', resp.content.decode('utf-8'))
        self.assertIn('третий (5)', resp.content.decode('utf-8'))

    def test_depricated_urls(self):
        PollFactory(question='Первый')
        poll = PollFactory(question='Второй')
        PollFactory(question='Третий')

        # by voteid
        resp = self.app.get('/votes/blank.html?voteid={}'.format(poll.id))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Второй', resp.content.decode('utf-8'))

        resp = self.app.get('/votes/blank.html?voteid=123456789')
        self.assertEqual(resp.status_code, 404)
        resp = self.app.get('/votes/blank.html?voteid=voteid')
        self.assertEqual(resp.status_code, 404)

        # prev/next
        resp = self.app.get('/votes/blank.html?pvoteid={}&type=prev'.format(poll.id))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Первый', resp.content.decode('utf-8'))

        resp = self.app.get('/votes/blank.html?pvoteid=123456789&type=prev')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Третий', resp.content.decode('utf-8'))

        resp = self.app.get('/votes/blank.html?pvoteid={}&type=next'.format(poll.id))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Третий', resp.content.decode('utf-8'))

        resp = self.app.get('/votes/blank.html?pvoteid=123456789&type=next')
        self.assertEqual(resp.status_code, 404)
        resp = self.app.get('/votes/blank.html?pvoteid=pvoteid&type=next')
        self.assertEqual(resp.status_code, 404)

        # without type
        resp = self.app.get('/votes/blank.html?pvoteid={}'.format(poll.id))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Второй', resp.content.decode('utf-8'))
