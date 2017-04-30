from apps.articles.models import Section, GENERIC_SECTIONS, NEWS
from apps.utils.jobs import SidebarContextJob, HeaderContextJob


class HeaderContextMixin(object):

    def get_header_context(self):
        return HeaderContextJob().get()


class PageContextMixin(HeaderContextMixin):

    def get_context_data(self, **kwargs):
        kwargs.update(
            self.get_header_context()
        )
        kwargs.update(
            SidebarContextJob().get()
        )
        return super().get_context_data(**kwargs)


class PdaPageContextMixin(object):

    def get_context_data(self, **kwargs):
        kwargs.update(
            sections=[GENERIC_SECTIONS[NEWS]] + list(Section.objects.navigate())
        )
        return super().get_context_data(**kwargs)
