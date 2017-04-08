from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.db.models import OuterRef, Subquery, Sum, IntegerField, Value
from django.db.models.functions import Coalesce

from apps.polls.models import Choice, Poll


@receiver(post_delete, sender=Choice)
def update_poll_sum_votes(sender, instance, **kwargs):
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
    Poll.objects.filter(id=instance.poll_id).update(**data)
