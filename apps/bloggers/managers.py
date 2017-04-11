from django.db import models


class BloggerQuerySet(models.QuerySet):

    def active(self):
        return self.filter(is_active=True)


class EntryQuerySet(models.QuerySet):

    def active(self):
        return self.filter(is_active=True, blogger__is_active=True)
