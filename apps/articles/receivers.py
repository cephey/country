from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from apps.articles.models import Comment, Article


@receiver((post_save, post_delete), sender=Comment)
def update_article_comments_count(sender, instance, **kwargs):
    count = Comment.objects.filter(article=instance.article_id).count()
    Article.objects.filter(id=instance.article_id).update(comments_count=count)
