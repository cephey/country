import factory
from apps.polls.models import Poll, Choice


class PollFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Poll

    question = factory.Faker('text', max_nb_chars=128, locale='ru_RU')


class ChoiceFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Choice

    poll = factory.SubFactory('apps.polls.factories.PollFactory')
    answer = factory.Faker('text', max_nb_chars=64, locale='ru_RU')
