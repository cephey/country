from django.test import TestCase, Client

from apps.articles.factories import ArticleFactory
from apps.tags.factories import TagFactory


class TagTestCase(TestCase):

    def setUp(self):
        self.app = Client()

    def test_tag_detail_page(self):
        tag1 = TagFactory(name='колибри')
        tag2 = TagFactory(name='воробей')

        ArticleFactory(title='Птицы', tags=[tag1, tag2])
        ArticleFactory(title='Северные', tags=[tag2])
        ArticleFactory(title='Южные', tags=[tag1])
        ArticleFactory(title='Западные', tags=[tag1, tag2], is_active=False)

        resp = self.app.get('/tags/{}/'.format(tag1.id))
        self.assertEqual(resp.status_code, 200)

        articles = resp.context['object_list']
        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0].title, 'Южные')
        self.assertEqual(articles[1].title, 'Птицы')
        self.assertEqual(resp.context['partition'], tag1)

        self.assertContains(resp, 'колибри')
        self.assertNotContains(resp, 'воробей')
