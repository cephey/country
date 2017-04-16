from django.test import TestCase, Client
from django.contrib.sessions.models import Session

from apps.votes.models import Vote
from apps.votes.factories import VoteFactory
from apps.polls.models import Poll, Choice
from apps.polls.factories import PollFactory, ChoiceFactory
from apps.articles.factories import ArticleFactory, CommentFactory
from apps.users.factories import UserFactory


class RatingTestCase(TestCase):

    def setUp(self):
        self.app = Client()

    def test_create_vote_article_user(self):
        article = ArticleFactory()

        user = UserFactory(username='andrey')
        user.set_password('secret')
        user.save()
        self.app.login(username='andrey', password='secret')

        resp = self.app.post('/votes/article/', {'object_id': article.id, 'score': 2},
                             HTTP_REFERER='/material/news/1/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/material/news/1/')

        votes = Vote.objects.all()
        self.assertEqual(len(votes), 1)
        self.assertEqual(votes[0].user, user)
        self.assertEqual(votes[0].object_id, article.id)
        self.assertEqual(votes[0].score, 2)

    def test_update_vote_article_user(self):
        article = ArticleFactory()

        user = UserFactory(username='andrey')
        user.set_password('secret')
        user.save()
        self.app.login(username='andrey', password='secret')

        VoteFactory(content_object=article, score=2, user=user)

        resp = self.app.post('/votes/article/', {'object_id': article.id, 'score': 3},
                             HTTP_REFERER='/material/news/1/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/material/news/1/')

        votes = Vote.objects.all()
        self.assertEqual(len(votes), 1)
        self.assertEqual(votes[0].user, user)
        self.assertEqual(votes[0].object_id, article.id)
        self.assertEqual(votes[0].score, 3)

    def test_create_vote_article_anonymous(self):
        article = ArticleFactory()

        self.app.get('/')  # create session_key
        token = Session.objects.first().session_key

        resp = self.app.post('/votes/article/', {'object_id': article.id, 'score': 4},
                             HTTP_REFERER='/material/news/1/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/material/news/1/')

        votes = Vote.objects.all()
        self.assertEqual(len(votes), 1)
        self.assertEqual(votes[0].token, token)
        self.assertEqual(votes[0].object_id, article.id)
        self.assertEqual(votes[0].score, 4)

    def test_update_vote_article_anonymous(self):
        article = ArticleFactory()

        self.app.get('/')  # create session_key
        token = Session.objects.first().session_key

        VoteFactory(content_object=article, score=2, token=token)

        resp = self.app.post('/votes/article/', {'object_id': article.id, 'score': 5},
                             HTTP_REFERER='/material/news/1/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/material/news/1/')

        votes = Vote.objects.all()
        self.assertEqual(len(votes), 1)
        self.assertEqual(votes[0].token, token)
        self.assertEqual(votes[0].object_id, article.id)
        self.assertEqual(votes[0].score, 5)

    def test_vote_atricle_fail(self):
        self.app.get('/')  # create session_key

        # fake article id
        resp = self.app.post('/votes/article/', {'object_id': 999999999, 'score': 1},
                             HTTP_REFERER='/material/news/1/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/material/news/1/')
        self.assertFalse(Vote.objects.exists())

        article = ArticleFactory()

        # bad score
        resp = self.app.post('/votes/article/', {'object_id': article.id, 'score': 8},
                             HTTP_REFERER='/material/news/{}/'.format(article.id), follow=True)
        url, status_code = resp.redirect_chain[0]
        self.assertEqual(status_code, 302)
        self.assertEqual(url, '/material/news/{}/'.format(article.id))
        self.assertFalse(Vote.objects.exists())
        self.assertContains(resp, 'Возможность оставить оценку временно недоступна')
