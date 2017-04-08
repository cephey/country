from django.db.models import Sum, Count, Avg, IntegerField, Value
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.contrib.contenttypes.models import ContentType

from apps.articles.models import Comment, Article
from apps.polls.models import Choice, Poll
from apps.votes.models import Vote


@receiver((post_save, post_delete), sender=Vote)
def update_vote_related_counters(sender, instance, **kwargs):
    article_ct = ContentType.objects.get_for_model(Article)
    comment_ct = ContentType.objects.get_for_model(Comment)
    choice_ct = ContentType.objects.get_for_model(Choice)

    if instance.content_type_id == comment_ct.id:
        data = {
            'karma': Coalesce(
                Subquery(Vote.objects
                         .filter(object_id=OuterRef('id'), content_type=comment_ct)
                         .order_by()
                         .values('object_id')
                         .annotate(sum=Sum('score'))
                         .values('sum'),
                         output_field=IntegerField()),
                Value(0),
                output_field=IntegerField())
        }
        Comment.objects.filter(id=instance.object_id).update(**data)

    elif instance.content_type_id == choice_ct.id:
        data = {
            'vote_count': Coalesce(
                Subquery(Vote.objects
                         .filter(object_id=OuterRef('id'), content_type=choice_ct)
                         .order_by()
                         .values('object_id')
                         .annotate(count=Count('id'))
                         .values('count'),
                         output_field=IntegerField()),
                Value(0),
                output_field=IntegerField())
        }
        Choice.objects.filter(id=instance.object_id).update(**data)

        data = {
            'sum_votes': Coalesce(
                Subquery(Choice.objects
                         .filter(poll=OuterRef('id'))
                         .order_by()
                         .values('poll')
                         .annotate(sum=Sum('vote_count'))
                         .values('sum'),
                         output_field=IntegerField()),
                Value(0),
                output_field=IntegerField())
        }
        Poll.objects.filter(choice__id=instance.object_id).update(**data)

    elif instance.content_type_id == article_ct.id:
        # TODO: bad part of code, can be made more optimally through the RawSQL, but I wanted to use ORM
        data = {
            'rating': Coalesce(
                Subquery(Vote.objects
                         .filter(object_id=OuterRef('id'), content_type=article_ct)
                         .order_by()
                         .values('object_id')
                         .annotate(avg=Avg('score'))
                         .values('avg'),
                         output_field=IntegerField()),
                Value(0),
                output_field=IntegerField()),
            'vote_count': Coalesce(
                Subquery(Vote.objects
                         .filter(object_id=OuterRef('id'), content_type=article_ct)
                         .order_by()
                         .values('object_id')
                         .annotate(count=Count('id'))
                         .values('count'),
                         output_field=IntegerField()),
                Value(0),
                output_field=IntegerField())
        }
        Article.objects.filter(id=instance.object_id).update(**data)
