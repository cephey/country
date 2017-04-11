import random
import factory
from faker import Faker
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

    @factory.post_generation
    def description(obj, create, extracted, **kwargs):
        if extracted:
            obj.description = extracted
        elif random.randint(0, 10):
            obj.description = Faker(locale='ru_RU').text(max_nb_chars=random.randint(128, 512))
