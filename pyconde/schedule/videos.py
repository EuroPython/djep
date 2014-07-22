"""
This module includes abstractions for various video services to be embedded on a
session page.
"""

import abc
import urllib
import logging
import requests
import re


LOG = logging.getLogger(__name__)


class VideoService(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def matches_link(self, url):
        pass

    @abc.abstractmethod
    def generate_embed_code(self, url):
        pass


class OEmbedSupportingVideoService(VideoService):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def generate_oembed_url(self, url):
        pass

    def generate_embed_code(self, url):
        oembed_url = self.generate_oembed_url(url)
        resp = requests.get(oembed_url).json()
        return resp['html']


class YouTubeService(OEmbedSupportingVideoService):
    def matches_link(self, url):
        return url.startswith('https://www.youtube.com/watch?v=') or url.startswith('http://www.youtube.com/watch?v=')

    def generate_oembed_url(self, url):
        query = urllib.urlencode({
            'url': url,
            'format': 'json'
            })
        return 'https://www.youtube.com/oembed?' + query

    def generate_embed_code(self, url):
        data = super(YouTubeService, self).generate_embed_code(url)
        return data.replace('src="http://', 'src="https://')


class PyVideoService(VideoService):
    video_re = re.compile(r'http://pyvideo\.org/video/(?P<id>\d+)/.*')

    def matches_link(self, url):
        return self.video_re.match(url) is not None

    def get_video_id(self, url):
        mo = self.video_re.match(url)
        if mo:
            return mo.group('id')

    def generate_embed_code(self, url):
        video_id = self.get_video_id(url)
        if video_id is None:
            return None
        data = requests.get('http://pyvideo.org/api/v1/video/{0}/'.format(video_id)).json

        # pyvideos is used as front for some other service like YouTube, use
        # the embed-code from the source.
        source_embed = generate_embed_code(data['source_url'])
        if not source_embed:
            source_embed = data['embed']
        return source_embed + '<br><a href="{0}">pyvideo.org</a>'.format(url)


_SERVICES = [YouTubeService(), PyVideoService()]


def generate_embed_code(url):
    for service in _SERVICES:
        if service.matches_link(url):
            try:
                return service.generate_embed_code(url)
            except Exception, e:
                LOG.exception(e)
    return None
