import factory
from apps.pages.models import Partition, Resource


class PartitionFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Partition

    name = factory.Faker('sentence', nb_words=2, locale='ru_RU')


class ResourceFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Resource

    partition = factory.SubFactory('apps.pages.factories.PartitionFactory')
    name = factory.Faker('sentence', nb_words=3, locale='ru_RU')
    logo = factory.django.ImageField(from_path='fixtures/i/ya.gif')
    url = factory.Faker('uri')
