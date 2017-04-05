from django.db.models import Sum
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType

from apps.articles.models import Comment
from apps.polls.models import Choice
from apps.votes.models import Vote


@receiver(post_save, sender=Vote)
def update_comment_karma(sender, instance, **kwargs):
    comment_ct = ContentType.objects.get_for_model(Comment)
    choice_ct = ContentType.objects.get_for_model(Choice)

    if instance.content_type == comment_ct:
        karma = (Vote.objects
                 .filter(object_id=instance.object_id, content_type=comment_ct)
                 .aggregate(sum=Sum('score')))
        Comment.objects.filter(id=instance.object_id).update(karma=karma['sum'])

    elif instance.content_type == choice_ct:
        vote_count = (Vote.objects
                      .filter(object_id=instance.object_id, content_type=choice_ct)
                      .aggregate(sum=Sum('score')))
        Choice.objects.filter(id=instance.object_id).update(vote_count=vote_count['sum'])
