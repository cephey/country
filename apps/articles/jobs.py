from cacheback.base import Job
from apps.articles.models import Article, Section, NAVIGATE_SECTIONS


class IndexSectionArticlesJob(Job):
    lifetime = 300  # 5 minutes
    cache_ttl = 24 * 3600  # 1 day
    fetch_on_miss = True

    def fetch(self):
        sections = Section.objects.filter(slug__in=NAVIGATE_SECTIONS)

        materials = {}
        for section in sections:
            materials[section.slug] = {
                'section': section,
                'articles': (Article.objects.visible().with_authors()
                             .select_related('section')
                             .filter(section=section)[:6])
            }
        return materials
