from django.test import TestCase
from apps.votes.models import Vote
from apps.votes.factories import VoteFactory
from apps.polls.models import Poll, Choice
from apps.polls.factories import PollFactory, ChoiceFactory
from apps.articles.factories import ArticleFactory, CommentFactory
from apps.articles.models import Article


class VoteTestCase(TestCase):

    def setUp(self):
        pass

    def test_polls_counters(self):
        poll = PollFactory()
        ChoiceFactory.create_batch(3, poll=poll)

        choice1, choice2, choice3 = Choice.objects.order_by('id')
        self.assertEqual(choice1.vote_count, 0)
        self.assertEqual(choice2.vote_count, 0)
        self.assertEqual(choice3.vote_count, 0)
        self.assertEqual(Poll.objects.first().sum_votes, 0)

        VoteFactory(content_object=choice1, score=1)
        VoteFactory(content_object=choice2, score=1)
        VoteFactory(content_object=choice1, score=1)

        choice1, choice2, choice3 = Choice.objects.order_by('id')
        self.assertEqual(choice1.vote_count, 2)
        self.assertEqual(choice2.vote_count, 1)
        self.assertEqual(choice3.vote_count, 0)
        self.assertEqual(Poll.objects.first().sum_votes, 3)

        choice2.delete()
        self.assertEqual(Poll.objects.first().sum_votes, 2)

        choice1.delete()
        self.assertEqual(Poll.objects.first().sum_votes, 0)

        choice3.delete()
        self.assertEqual(Poll.objects.first().sum_votes, 0)

    def test_article_rating(self):
        article = ArticleFactory()

        VoteFactory(content_object=article, score=3)
        VoteFactory(content_object=article, score=5)

        article.refresh_from_db()
        self.assertEqual(article.rating, 4)
        self.assertEqual(article.vote_count, 2)

    def test_comment_likes(self):
        comment = CommentFactory()

        for score in (1, -1, 1, 1):
            VoteFactory(content_object=comment, score=score)
        comment.refresh_from_db()
        self.assertEqual(comment.karma, 2)

        Vote.objects.all().delete()
        comment.refresh_from_db()
        self.assertEqual(comment.karma, 0)
