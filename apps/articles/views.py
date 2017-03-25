from django.views.generic import TemplateView
from apps.authors.models import Author
from apps.articles.models import Article, Section, NAVIGATE_SECTIONS, Notice
from apps.polls.models import Poll
from apps.bloggers.models import Entry


class IndexView(TemplateView):
    template_name = 'articles/index.html'

    def get_context_data(self, **kwargs):
        kwargs.update(
            sections=Section.objects.filter(slug__in=NAVIGATE_SECTIONS).order_by('id'),
            marquee=Article.objects.filter(section__slug='news').order_by('-publish_date').first(),

            news_list=Article.objects.filter(section__slug='news').order_by('?')[:3],  # order by vote_sum?

            main_news=Article.objects.filter(section__slug='news').order_by('-publish_date').first(),
            main_material=Article.objects.filter(section__slug='best').order_by('-publish_date').first(),

            materials={
                'politic': Section.objects.get(slug='politic'),
                'moscow': Section.objects.get(slug='moscow'),
                'economic': Section.objects.get(slug='economic'),
                'region': Section.objects.get(slug='region'),
                'society': Section.objects.get(slug='society'),
                'power': Section.objects.get(slug='power'),
                'fpolitic': Section.objects.get(slug='fpolitic'),
                'kompromat': Section.objects.get(slug='kompromat'),
            },
            poll=Poll.objects.order_by('?').first(),
            video_articles=Article.objects.filter(video__isnull=False)[:2],
            news_articles=Article.objects.filter(section__slug='news').order_by('?')[:10],  # order by vote_sum?
            notices=Notice.objects.all()[:3],
            entries=Entry.objects.order_by('?')[:5],
            authors=Author.objects.order_by('last_name')[:15]
        )
        # 6 articles for each section
        # order by data (+ shuffle)

        kwargs['text_banner'] = self.get_text_banner()
        return super().get_context_data(**kwargs)

    def get_text_banner(self):
        """
        my $self = shift;
        return $self->get_text_banner_by_tbn($self->get_tbn_by_uri(@_));
        my $sape = new Forum::Export::Links(
            user => 'c55bf3fc219b9610c2b8abde2d8ed171',
            host => 'forum.msk.ru',
            charset => 'koi8-r',
            timeout => 600,
            filename => $state->data_dir.'/links.db',
            uri => shift || '/index.html',
            remote_ip => '80.93.56.97',
            force_show_code => 1,
        );
        my $links = $sape->get_links( count => 10 );
        return $links=~/\S/ ? $links : undef;
        """
        return ''


class SectionView(TemplateView):
    template_name = 'articles/index.html'


class RssView(TemplateView):
    template_name = 'articles/rss.html'
