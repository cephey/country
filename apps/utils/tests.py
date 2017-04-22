import responses
from django.test import TestCase
from apps.utils.video import VideoHelper


class VideoHelperTestCase(TestCase):

    def test_youtube_thumbnail(self):
        url = 'https://www.youtube.com/watch?v=Google123'
        thumbnail = VideoHelper(url).thumbnail
        self.assertEqual(thumbnail, 'http://img.youtube.com/vi/Google123/default.jpg')

    @responses.activate
    def test_rutube_thumbnail(self):
        responses.add(responses.GET, 'http://rutube.ru/api/video/6fd81c1c212c002673280850a1c56415/',
                      body=open('fixtures/json/rutube.json').read())

        url = 'http://rutube.ru/video/6fd81c1c212c002673280850a1c56415/'
        thumbnail = VideoHelper(url).thumbnail
        self.assertEqual(thumbnail, 'http://pic.rutube.ru/video/3f/79/3f7991857b0ae5621684681640b0865d.jpg')

    @responses.activate
    def test_vimeo_thumbnail(self):
        responses.add(responses.GET, 'http://vimeo.com/api/v2/video/55028438.json',
                      body=open('fixtures/json/vimeo.json').read())

        url = 'http://vimeo.com/55028438'
        thumbnail = VideoHelper(url).thumbnail
        self.assertEqual(thumbnail, 'http://i.vimeocdn.com/video/481108654_200x150.jpg')
