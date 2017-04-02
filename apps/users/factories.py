import factory
from django.contrib.auth import get_user_model


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = get_user_model()

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    avatar = factory.django.ImageField(from_path='fixtures/i/flag.jpg')
