from django.db import models


class ResourceTypeQuerySet(models.QuerySet):

    def active(self):
        return self.filter(is_active=True)


class ResourceQuerySet(models.QuerySet):

    def active(self):
        return self.filter(is_active=True)
