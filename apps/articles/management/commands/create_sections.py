from django.core.management.base import BaseCommand

from apps.articles.models import Section


class Command(BaseCommand):
    help = 'Create sections (common and video(non partner))'

    def handle(self, *args, **kwargs):
        self.stdout.write('Start...')

        sections = [
            Section(name='Политический расклад', slug='politic', ext_id=111),
            Section(name='Экономическая реальность', slug='economic', ext_id=112),
            Section(name='Жизнь регионов', slug='region', ext_id=119),
            Section(name='Общество и его культура', slug='society', ext_id=122),
            Section(name='Силовые структуры', slug='power', ext_id=121),
            Section(name='Особенности внешней политики', slug='fpolitic', ext_id=118),
            Section(name='Компрометирующие материалы', slug='kompromat', ext_id=120),
            Section(name='Московский листок', slug='moscow', ext_id=10578361),

            # video
            Section(name='Новости политики', slug='video_politic', is_video=True, ext_id=8221433),
            Section(name='Экономический расклад', slug='video_economic', is_video=True, ext_id=8221434),
            Section(name='Проиcшествия', slug='video_accidents', is_video=True, ext_id=8221447),
            Section(name='Внешняя политика', slug='video_fpolitic', is_video=True, ext_id=8221449),
            Section(name='Общество и его культура', slug='video_society', is_video=True, ext_id=8221435),
            Section(name='Народное видео', slug='video_national', is_video=True, ext_id=8221436),
        ]
        Section.objects.bulk_create(sections, batch_size=100)
        self.stdout.write('End...')
