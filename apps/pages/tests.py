from django.test import TestCase, Client
from apps.pages.factories import PartitionFactory, ResourceFactory


class PagesTestCase(TestCase):

    def setUp(self):
        self.app = Client()

    def test_about_page_200(self):
        resp = self.app.get('/about/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Свободы хотим, демократии и прогресса')

    def test_advert_page_200(self):
        resp = self.app.get('/advert/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Реклама на главной странице')

    def test_opposition_index_page(self):
        part1 = PartitionFactory(name='Физика')
        part2 = PartitionFactory(name='Химия')
        part3 = PartitionFactory(name='Математика', is_active=False)

        ResourceFactory(partition=part1, name='Термодинамика', rating=1)
        ResourceFactory(partition=part1, name='Электромагнетизм', rating=2)
        ResourceFactory(partition=part1, name='Оптика', rating=3, is_active=False)
        ResourceFactory(partition=part2, name='Элементы', rating=6)
        ResourceFactory(partition=part2, name='Органическая', rating=5)
        ResourceFactory(partition=part3, name='Алгебра', rating=4)

        resp = self.app.get('/opposition_hoop/')
        self.assertEqual(resp.status_code, 200)

        # check template
        self.assertContains(resp, 'Физика')
        self.assertContains(resp, 'Химия')
        self.assertNotContains(resp, 'Математика')

        self.assertContains(resp, 'Термодинамика')
        self.assertContains(resp, 'Элементы')
        self.assertNotContains(resp, 'Оптика')
        self.assertNotContains(resp, 'Алгебра')

        self.assertContains(resp, 'Наши кнопки')

        # check context
        partitions = resp.context['partitions']
        self.assertEqual(len(partitions), 2)
        self.assertEqual(partitions[0]['partition'].name, 'Физика')
        self.assertEqual(['Электромагнетизм', 'Термодинамика'], [r.name for r in partitions[0]['resources']])
        self.assertEqual(partitions[1]['partition'].name, 'Химия')
        self.assertEqual(['Элементы', 'Органическая'], [r.name for r in partitions[1]['resources']])

        new_resources = [r.name for r in resp.context['new_resources']]
        self.assertEqual(['Органическая', 'Элементы', 'Электромагнетизм', 'Термодинамика'], new_resources)

    def test_partition_page(self):
        part = PartitionFactory(name='Каша')

        ResourceFactory(partition=part, name='Манка', rating=2)
        ResourceFactory(partition=part, name='Греча', rating=4)
        ResourceFactory(partition=part, name='Овсянка', rating=1, is_active=False)
        ResourceFactory(partition=part, name='Перловка', rating=3)

        resp = self.app.get('/opposition_hoop/{}/'.format(part.id))
        self.assertEqual(resp.status_code, 200)

        # check template
        self.assertContains(resp, 'Каша')
        self.assertContains(resp, 'Манка')
        self.assertContains(resp, 'Греча')
        self.assertContains(resp, 'Перловка')
        self.assertNotContains(resp, 'Овсянка')

        # check context
        self.assertEqual(resp.context['partition'], part)
        self.assertEqual(['Греча', 'Перловка', 'Манка'], [r.name for r in resp.context['resource_list']])

    def test_partition_404(self):
        part = PartitionFactory(is_active=False)
        resp = self.app.get('/opposition_hoop/{}/'.format(part.id))
        self.assertEqual(resp.status_code, 404)

    def test_deprecated_url(self):
        part = PartitionFactory()
        resp = self.app.get('/opposition_hoop/?part={}'.format(part.id))
        self.assertEqual(resp.status_code, 301)
        self.assertEqual(resp.url, '/opposition_hoop/{}/'.format(part.id))
