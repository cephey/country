from django.core.management.base import BaseCommand

from apps.pages.models import Partition


class Command(BaseCommand):
    help = 'Create opposition partitions'

    def handle(self, *args, **kwargs):
        self.stdout.write('Start...')

        partitions = [
            Partition(name='Персональные сайты', ext_id=125),
            Partition(name='Партии и общественные движения', ext_id=128),
            Partition(name='Оппозиционные СМИ', ext_id=129),
            Partition(name='Аналитика', ext_id=130),
            Partition(name='Креативные проекты', ext_id=131),
            Partition(name='Блоги и форумы', ext_id=582256),
            Partition(name='Музыка', ext_id=132),
            Partition(name='Литература и искусство', ext_id=133),
            Partition(name='Региональные организации', ext_id=134),
            Partition(name='Библиотеки', ext_id=136),
            Partition(name='История', ext_id=135),
        ]
        Partition.objects.bulk_create(partitions, batch_size=100)
        self.stdout.write('End...')
