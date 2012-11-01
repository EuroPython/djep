"""
This module includes abstractions for various video services to be embedded on a
session page.
"""

import abc
import urlparse
import urllib
import logging
import requests


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
        return requests.get(oembed_url).json['html']


class YouTubeService(OEmbedSupportingVideoService):
    def matches_link(self, url):
        return url.startswith('https://www.youtube.com/watch?v=') or url.startswith('http://www.youtube.com/watch?v=')

    def generate_oembed_url(self, url):
        video_id = urlparse.parse_qs(urlparse.urlparse(url).query)['v']
        query = urllib.urlencode({
            'url': url,
            'format': 'json'
            })
        return 'http://www.youtube.com/oembed?' + query

_SERVICES = [YouTubeService()]

def generate_embed_code(url):
    for service in _SERVICES:
        if service.matches_link(url):
            try:
                return service.generate_embed_code(url)
            except Exception, e:
                LOG.error(e)
    return None
