from django.db import models
from django.db.models import Case, When, Value, IntegerField


class SectionQuerySet(models.QuerySet):

    def active(self):
        return self.filter(is_active=True)

    def navigate(self):
        from apps.articles.models import NAVIGATE_SECTIONS

        case_exp = [When(slug=slug, then=Value(i)) for i, slug in enumerate(NAVIGATE_SECTIONS)]
        return (self.active()
                .filter(slug__in=NAVIGATE_SECTIONS)
                .annotate(custom_order=Case(*case_exp,
                                            default=Value(len(NAVIGATE_SECTIONS)),
                                            output_field=IntegerField()))
                .order_by('custom_order'))


class ArticleQuerySet(models.QuerySet):

    def visible(self):
        return self.filter(is_active=True, status='approved')

    def open(self):
        return self.visible().filter(discussion_status='open')

    def with_authors(self):
        return self.prefetch_related('authors')


class CommentQuerySet(models.QuerySet):

    def active(self):
        return self.filter(is_active=True)


class NoticeQuerySet(models.QuerySet):

    def visible(self):
        return self.filter(status='approved')
