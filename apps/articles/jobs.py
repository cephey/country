from apps.articles.models import Article, Section, NAVIGATE_SECTIONS, VIDEO_SECTIONS
from apps.utils.jobs import Job


class IndexSectionArticlesJob(Job):

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


class VideoArticlesJob(Job):

    def fetch(self):
        sections = Section.objects.filter(slug__in=VIDEO_SECTIONS, is_video=True)

        materials = {}
        for section in sections:
            if section.slug in ('video_fpolitic', 'video_national'):
                n = 5
            elif section.slug.startswith('video_partner'):
                n = 2
            else:
                n = 3
            materials[section.slug] = {
                'section': section,
                'articles': (Article.objects.visible().with_authors()
                             .select_related('section')
                             .filter(section=section)[:n])
            }
        return materials


class InSectionJob(Job):

    def fetch(self):
        data = []
        for slug in NAVIGATE_SECTIONS:
            article = (Article.objects.visible().with_authors()
                       .filter(section__slug=slug)
                       .select_related('section')
                       .order_by('-publish_date')
                       .first())
            if article:
                data.append(article)
        return data
