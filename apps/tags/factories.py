import factory
from apps.tags.models import Tag, TaggedItem


class TagFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Tag
        django_get_or_create = ('name',)

    name = factory.Faker('word', locale='ru_RU')


class TaggedItemFactory(factory.DjangoModelFactory):

    class Meta:
        model = TaggedItem

    tag = factory.SubFactory('apps.tags.factories.TagFactory')
