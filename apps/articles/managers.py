from django.db import models


class SectionQuerySet(models.QuerySet):

    def active(self):
        return self.filter(is_active=True)


class ArticleQuerySet(models.QuerySet):

    def visible(self):
        return self.filter(is_active=True, status='approved')

    def open(self):
        return self.visible().filter(discussion_status='open')


class CommentQuerySet(models.QuerySet):

    def active(self):
        return self.filter(is_active=True)


class NoticeQuerySet(models.QuerySet):

    def visible(self):
        return self.filter(status='approved')
