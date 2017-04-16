from django.test import TestCase, Client

from apps.votes.models import Vote
from apps.users.factories import UserFactory
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
        self.assertContains(resp, 'Результаты голосования')
        self.assertContains(resp, 'Как так?')

        self.assertContains(resp, 'font-size:90%;width:20%;background-color:#990000')
        self.assertContains(resp, 'первый (2)')

        self.assertContains(resp, 'font-size:90%;width:30%;background-color:#990000')
        self.assertContains(resp, 'второй (3)')

        self.assertContains(resp, 'font-size:90%;width:50%;background-color:#990000')
        self.assertContains(resp, 'третий (5)')

    def test_create_vote_user(self):
        user = UserFactory(username='andrey')
        user.set_password('secret')
        user.save()
        self.app.login(username='andrey', password='secret')

        poll = PollFactory()
        choice = ChoiceFactory(poll=poll)
        resp = self.app.post('/polls/', {'poll_id': poll.id, 'choices': choice.id})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/polls/{}/'.format(poll.id))

        votes = Vote.objects.all()
        self.assertEqual(len(votes), 1)
        self.assertEqual(votes[0].content_object, choice)

        choice.refresh_from_db()
        self.assertEqual(choice.vote_count, 1)
        poll.refresh_from_db()
        self.assertEqual(poll.sum_votes, 1)

        # try again: has no effect
        resp = self.app.post('/polls/', {'poll_id': poll.id, 'choices': choice.id})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Vote.objects.count(), 1)

        choice.refresh_from_db()
        self.assertEqual(choice.vote_count, 1)
        poll.refresh_from_db()
        self.assertEqual(poll.sum_votes, 1)

    def test_create_vote_anonymous(self):
        poll = PollFactory()
        choice = ChoiceFactory(poll=poll)

        resp = self.app.post('/polls/', {'poll_id': poll.id, 'choices': choice.id})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/polls/{}/'.format(poll.id))
        self.assertEqual(Vote.objects.count(), 1)

        # try again: has no effect
        resp = self.app.post('/polls/', {'poll_id': poll.id, 'choices': choice.id})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Vote.objects.count(), 1)

    def test_depricated_urls(self):
        PollFactory(question='Первый')
        poll = PollFactory(question='Второй')
        PollFactory(question='Третий')

        # by voteid
        resp = self.app.get('/votes/blank.html?voteid={}'.format(poll.id))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Второй')

        resp = self.app.get('/votes/blank.html?voteid=123456789')
        self.assertEqual(resp.status_code, 404)
        resp = self.app.get('/votes/blank.html?voteid=voteid')
        self.assertEqual(resp.status_code, 404)

        # prev/next
        resp = self.app.get('/votes/blank.html?pvoteid={}&type=prev'.format(poll.id))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Первый')

        resp = self.app.get('/votes/blank.html?pvoteid=123456789&type=prev')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Третий')

        resp = self.app.get('/votes/blank.html?pvoteid={}&type=next'.format(poll.id))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Третий')

        resp = self.app.get('/votes/blank.html?pvoteid=123456789&type=next')
        self.assertEqual(resp.status_code, 404)
        resp = self.app.get('/votes/blank.html?pvoteid=pvoteid&type=next')
        self.assertEqual(resp.status_code, 404)

        # without type
        resp = self.app.get('/votes/blank.html?pvoteid={}'.format(poll.id))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Второй')
