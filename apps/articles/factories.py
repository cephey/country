import random
import factory
from faker import Faker
from django.utils import timezone

from apps.articles.models import Section, Article, Notice, Comment


class SectionFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Section

    name = factory.Faker('sentence', nb_words=2, locale='ru_RU')
    slug = factory.Faker('slug')


class ArticleFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Article

    title = factory.Faker('sentence', nb_words=3, locale='ru_RU')
    section = factory.SubFactory('apps.articles.factories.SectionFactory')
    publish_date = factory.LazyFunction(timezone.now)
    image = factory.django.ImageField(from_path='fixtures/i/flag.jpg')

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

    @factory.post_generation
    def tags(obj, create, extracted, **kwargs):
        from apps.tags.factories import TaggedItemFactory
        if extracted:
            for tag in extracted:
                TaggedItemFactory(tag=tag, content_object=obj)

    @factory.post_generation
    def with_tag(obj, create, extracted, **kwargs):
        from apps.tags.factories import TaggedItemFactory
        if extracted:
            TaggedItemFactory(content_object=obj)

    @factory.post_generation
    def description(obj, create, extracted, **kwargs):
        if not extracted and random.randint(0, 2):
            obj.description = Faker(locale='ru_RU').text(max_nb_chars=random.randint(128, 1024))

    @factory.post_generation
    def content(obj, create, extracted, **kwargs):
        if not extracted:
            obj.content = Faker(locale='ru_RU').text(max_nb_chars=random.randint(256, 2048))


class CommentFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Comment

    article = factory.SubFactory('apps.articles.factories.ArticleFactory')
    username = factory.Faker('name', locale='ru_RU')

    @factory.post_generation
    def title(obj, create, extracted, **kwargs):
        if not extracted and random.randint(0, 5):
            obj.title = Faker(locale='ru_RU').sentence(nb_words=3)

    @factory.post_generation
    def content(obj, create, extracted, **kwargs):
        if not extracted:
            obj.content = Faker(locale='ru_RU').text(max_nb_chars=random.randint(128, 512))


class NoticeFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Notice

    content = factory.Faker('text', max_nb_chars=256, locale='ru_RU')
