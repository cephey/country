from urllib.parse import urlparse, parse_qs
from model_utils import Choices
import requests
import logging

logger = logging.getLogger(__name__)

VIDEO_PROVIDERS = Choices(
    (1, 'youtube', 'YouTube'),
    (2, 'rutube', 'Rutube'),
    (3, 'vimeo', 'Vimeo')
)


class UnknownProvider(Exception):
    pass


class VideoHelper(object):
    provider = None
    url = None

    def __init__(self, url):
        self.url = url
        self._parse_provider()

    @property
    def iframe_code(self):
        if self.provider == VIDEO_PROVIDERS.youtube:
            code = self.get_youtube_video_code()
            return '<iframe width="560" height="315" src="https://www.youtube.com/embed/{}" ' \
                   'frameborder="0" allowfullscreen></iframe>'.format(code)

        elif self.provider == VIDEO_PROVIDERS.rutube:
            code = self.get_generic_video_code()
            return '<iframe width="720" height="405" src="//rutube.ru/play/embed/{}?sTitle=false&sAuthor=false" ' \
                   'frameborder="0" webkitAllowFullScreen mozallowfullscreen allowfullscreen></iframe>'.format(code)

        elif self.provider == VIDEO_PROVIDERS.vimeo:
            code = self.get_generic_video_code()
            return '<iframe width="640" height="360" src="https://player.vimeo.com/video/{}?byline=0" ' \
                   'frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>'.format(code)
        return ''

    @property
    def thumbnail(self):
        if self.provider == VIDEO_PROVIDERS.youtube:
            code = self.get_youtube_video_code()
            return 'http://img.youtube.com/vi/{}/default.jpg'.format(code)

        elif self.provider == VIDEO_PROVIDERS.rutube:
            code = self.get_generic_video_code()
            resp = requests.get('http://rutube.ru/api/video/{}/?format=json'.format(code))
            if resp.status_code == 200:
                try:
                    return resp.json()['thumbnail_url']
                except KeyError:
                    pass
            return ''

        elif self.provider == VIDEO_PROVIDERS.vimeo:
            code = self.get_generic_video_code()
            resp = requests.get('http://vimeo.com/api/v2/video/{}.json'.format(code))
            if resp.status_code == 200:
                try:
                    return resp.json()[0]['thumbnail_medium']
                except (IndexError, KeyError):
                    pass
            return ''
        return ''

    def _parse_provider(self):
        domain = urlparse(self.url).netloc.lower()
        if 'youtube' in domain:
            self.provider = VIDEO_PROVIDERS.youtube
        elif 'rutube' in domain:
            self.provider = VIDEO_PROVIDERS.rutube
        elif 'vimeo' in domain:
            self.provider = VIDEO_PROVIDERS.vimeo
        else:
            raise UnknownProvider('Received unknown provider {}'.format(domain))

    def get_youtube_video_code(self):
        query_string = urlparse(self.url).query
        query_dict = parse_qs(query_string)
        code = query_dict.get('v')
        if isinstance(code, (list, tuple)):
            return code[0]
        return code

    def get_generic_video_code(self):
        path_list = [p for p in urlparse(self.url).path.split('/') if p]
        return path_list[-1]
