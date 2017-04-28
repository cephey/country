from django.db import models


class PollQuerySet(models.QuerySet):

    def active(self):
        return self.filter(is_active=True)
