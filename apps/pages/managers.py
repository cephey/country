from django.db import models


class PartitionQuerySet(models.QuerySet):

    def active(self):
        return self.filter(is_active=True)


class ResourceQuerySet(models.QuerySet):

    def active(self):
        return self.filter(is_active=True, partition__is_active=True)
