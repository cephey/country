import factory
from apps.pages.models import ResourceType, Resource


class ResourceTypeFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = ResourceType

    name = factory.Faker('sentence', nb_words=2, locale='ru_RU')


class ResourceFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Resource

    type = factory.SubFactory('apps.pages.factories.ResourceTypeFactory')
    name = factory.Faker('sentence', nb_words=3, locale='ru_RU')
    logo = factory.django.ImageField(from_path='fixtures/i/ya.gif')
    url = factory.Faker('uri')
