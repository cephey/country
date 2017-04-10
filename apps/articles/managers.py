from django.db import models


class ArticleQuerySet(models.QuerySet):

    def visible(self):
        return self.filter(is_active=True, status='approved')
