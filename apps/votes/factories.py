import factory
from apps.votes.models import Vote


class VoteFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Vote

    score = 1
