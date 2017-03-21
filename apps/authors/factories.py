import factory
from apps.authors.models import Author


class AuthorFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Author

    first_name = factory.Faker('first_name', locale='ru_RU')
    last_name = factory.Faker('last_name', locale='ru_RU')
    description = factory.Faker('paragraph', nb_sentences=3, locale='ru_RU')
    photo = factory.django.ImageField(from_path='fixtures/i/flag.jpg')
