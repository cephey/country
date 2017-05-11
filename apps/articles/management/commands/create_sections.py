from django.core.management.base import BaseCommand

from apps.articles.models import Section


class Command(BaseCommand):
    help = 'Create sections (common and video(non partner))'

    def handle(self, *args, **kwargs):
        self.stdout.write('Start...')

        sections = [
            Section(name='Политический расклад', slug='politic'),
            Section(name='Экономическая реальность', slug='economic'),
            Section(name='Жизнь регионов', slug='region'),
            Section(name='Общество и его культура', slug='society'),
            Section(name='Силовые структуры', slug='power'),
            Section(name='Особенности внешней политики', slug='fpolitic'),
            Section(name='Компрометирующие материалы', slug='kompromat'),
            Section(name='Московский листок', slug='moscow'),

            # video
            Section(name='Новости политики', slug='video_politic'),
            Section(name='Экономический расклад', slug='video_economic'),
            Section(name='Проиcшествия', slug='video_accidents'),
            Section(name='Внешняя политика', slug='video_fpolitic'),
            Section(name='Общество и его культура', slug='video_society'),
            Section(name='Народное видео', slug='video_national'),
        ]
        Section.objects.bulk_create(sections, batch_size=100)
        self.stdout.write('End...')
