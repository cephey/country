import os
from django.conf import settings
from django.test import TestCase, Client
from django.core.management import call_command

from apps.articles.factories import ArticleFactory
from apps.authors.factories import AuthorFactory
from apps.authors.models import Author


class AuthorTestCase(TestCase):

    def setUp(self):
        self.app = Client()

    def test_detail_page(self):
        author = AuthorFactory(first_name='Игорь', last_name='Светлов',
                               description='Родился, женился и т.д.')

        ArticleFactory(authors=[author], title='Суббота')
        ArticleFactory(authors=[author], title='Воскресенье')
        ArticleFactory(authors=[author], is_active=False)
        ArticleFactory(with_author=True)

        resp = self.app.get('/author/{}/'.format(author.id))
        self.assertEqual(resp.status_code, 200)

        articles = resp.context['obj_atricles']
        self.assertEqual(len(articles), 2)
        self.assertEqual(resp.context['object'], author)

        self.assertContains(resp, 'Автор - Светлов Игорь')
        self.assertContains(resp, 'Об авторе')
        self.assertContains(resp, 'Родился, женился и т.д.')

        self.assertContains(resp, 'Последние статьи автора')
        self.assertContains(resp, 'Суббота')
        self.assertContains(resp, 'Воскресенье')

    def test_deprecated_url(self):
        author = AuthorFactory(first_name='Ян', last_name='Ин')
        resp = self.app.get('/author/{}/'.format(author.id))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['object'], author)
        self.assertContains(resp, 'Автор - Ин Ян')


class ImportTestCase(TestCase):

    def test_import_authors(self):
        call_command(
            'migrate_authors',
            path=os.path.join(settings.BASE_DIR, 'fixtures/csv/documents.csv')
        )
        authors = Author.objects.order_by('id')
        self.assertEqual(len(authors), 4)

        self.assertEqual(authors[0].first_name, 'Антон')
        self.assertEqual(authors[0].last_name, 'Суриков')
        self.assertIn('советника Российской Федерации 1 класса', authors[0].description)
        self.assertFalse(authors[0].is_active)
        self.assertEqual(authors[0].ext_id, 13)

        self.assertEqual(authors[1].last_name, 'Морозова')
        self.assertIn('кто Ленина любит и почитает', authors[1].description)

        self.assertEqual(authors[2].first_name, 'Игорь')
        self.assertTrue(authors[2].is_active)

        self.assertEqual(authors[3].last_name, 'Делягин')
        self.assertEqual(authors[3].ext_id, 10127171)
