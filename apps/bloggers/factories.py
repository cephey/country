import factory
from apps.bloggers.models import Blogger, Entry


class BloggerFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Blogger

    first_name = factory.Faker('first_name', locale='ru_RU')
    last_name = factory.Faker('last_name', locale='ru_RU')
    link = factory.Faker('uri')
    photo = factory.django.ImageField(from_path='fixtures/i/flag.jpg')


class EntryFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Entry

    title = factory.Faker('sentence', nb_words=3, locale='ru_RU')
    blogger = factory.SubFactory('apps.bloggers.factories.BloggerFactory')
    link = factory.Faker('uri')
