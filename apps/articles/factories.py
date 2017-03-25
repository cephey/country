import factory
from django.utils import timezone

from apps.articles.models import Section, Article, Notice


class SectionFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Section

    name = factory.Faker('sentence', nb_words=2, locale='ru_RU')
    slug = factory.Faker('slug')


class ArticleFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Article

    title = factory.Faker('sentence', nb_words=3, locale='ru_RU')
    content = factory.Faker('text', max_nb_chars=256, locale='ru_RU')
    section = factory.SubFactory('apps.articles.factories.SectionFactory')
    publish_date = factory.LazyFunction(timezone.now)

    @factory.post_generation
    def authors(obj, create, extracted, **kwargs):
        if extracted:
            for author in extracted:
                obj.authors.add(author)

    @factory.post_generation
    def with_author(obj, create, extracted, **kwargs):
        from apps.authors.factories import AuthorFactory
        if extracted:
            author = AuthorFactory()
            obj.authors.add(author)


class NoticeFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Notice

    content = factory.Faker('text', max_nb_chars=256, locale='ru_RU')
