# -*- encoding: utf-8 -*-
"""
This module abstracts various slide sharing services like SlideShare and
SpeakerDeck and provides functionality to extract embed-code from a document's
perma-link.
"""

import requests
from bs4 import BeautifulSoup
import urllib
import re
import abc
import logging


LOG = logging.getLogger(__name__)
RE_PREZI_URL = re.compile(r'^http://prezi.com/([a-zA-z0-9]+)/.*/$')


class AbstractSlideService(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def matches_link(self, link):
        """
        This method is used to bind an URL to a service. If it returns true
        for a given link, the service can process the link.
        """
        pass

    @abc.abstractmethod
    def generate_embed_code(self, link):
        """
        Generates the embed code for the given link.
        """
        pass


class AbstractOEmbedEnabledService(AbstractSlideService):
    """
    If the service provides a JSON OEmbed endpoint, this abstract class
    can be used for it. See the SlideShareService for an example.
    """

    def get_oembed_url(self, link):
        return link

    def generate_embed_code(self, link):
        oembed_url = self.get_oembed_url(link)
        return requests.get(oembed_url).json()['html']


class SlideShareService(AbstractOEmbedEnabledService):
    """
    Slideshare supports oembed URLs through a proxy.
    """

    def matches_link(self, link):
        return link.startswith("http://www.slideshare.net") or link.startswith("https://www.slideshare.net")

    def get_oembed_url(self, link):
        return '''https://www.slideshare.net/api/oembed/2?''' + urllib.urlencode((
            ('format', 'json'),
            ('url', link)
            ))


class SpeakerDeckOEmbedService(AbstractOEmbedEnabledService):
    def matches_link(self, link):
        return link.startswith('https://speakerdeck.com') or link.startswith('http://speakerdeck.com')

    def get_oembed_url(self, link):
        return '''https://speakerdeck.com/oembed.json?''' + urllib.urlencode((
            ('url', link),
            ))


class SpeakerDeckService(AbstractSlideService):
    """
    While SpeakerDeck also provides OEmbed functionality, it doesn't allow for
    flexible dimensions so this one should be used if possible and the OEmbed
    implementation is only active as a fallback if this one throws an exception
    which can be the case if SpeakerDeck changes their markup strukture.
    """
    def matches_link(self, link):
        return link.startswith('https://speakerdeck.com') or link.startswith('http://speakerdeck.com')

    def generate_embed_code(self, link, doc=None):
        """
        Speakerdeck sadly doesn't expose any ID except for the title of the
        document through the URL, so we have to get the embed code the hard
        way by parsing the actual website.
        """
        if doc is None:
            doc = requests.get(link).text
        soup = BeautifulSoup(doc)
        container = soup.find('section', {'id': 'presentation'})
        if container is None:
            container = soup.find('section', {'id': 'talk'})
        if container is None:
            container = soup.find('div', {'id': 'content'})
        if container is None:
            raise RuntimeError("Unexpected markup on Speakerdeck page")
        embed_elem = container.find('div', {'class': 'speakerdeck-embed'})
        return """<script async class="speakerdeck-embed" data-id="{id}" data-ratio="{ratio}" src="//speakerdeck.com/assets/embed.js"></script>""".format(
            id=embed_elem['data-id'],
            ratio=embed_elem['data-ratio']
            )


class PreziService(AbstractSlideService):
    def matches_link(self, link):
        return link.startswith('http://prezi.com/')

    def extract_id(self, link):
        mo = RE_PREZI_URL.search(link)
        if mo is not None:
            return mo.group(1)
        return None

    def generate_embed_code(self, link):
        embed_id = self.extract_id(link)
        if not embed_id:
            return None
        return '''<div class="prezi-player"><style type="text/css" media="screen">.prezi-player { width: 550px; } .prezi-player-links { text-align: center; }</style><object id="prezi_%(id)s" name="prezi_%(id)s" classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" width="550" height="400"><param name="movie" value="http://prezi.com/bin/preziloader.swf"/><param name="allowfullscreen" value="true"/><param name="allowFullScreenInteractive" value="true"/><param name="allowscriptaccess" value="always"/><param name="wmode" value="direct"/><param name="bgcolor" value="#ffffff"/><param name="flashvars" value="prezi_id=%(id)s&amp;lock_to_path=0&amp;color=ffffff&amp;autoplay=no&amp;autohide_ctrls=0"/><embed id="preziEmbed_%(id)s" name="preziEmbed_%(id)s" src="http://prezi.com/bin/preziloader.swf" type="application/x-shockwave-flash" allowfullscreen="true" allowFullScreenInteractive="true" allowscriptaccess="always" width="550" height="400" bgcolor="#ffffff" flashvars="prezi_id=%(id)s&amp;lock_to_path=0&amp;color=ffffff&amp;autoplay=no&amp;autohide_ctrls=0"></embed></object><div class="prezi-player-links"><p><a title="Slides" href="%(url)s">Slides</a> on <a href="http://prezi.com">Prezi</a></p></div></div>''' % dict(id=embed_id, url=link)


_SERVICES = [SlideShareService(), SpeakerDeckService(), SpeakerDeckOEmbedService(), PreziService()]


def generate_embed_code(link):
    for service in _SERVICES:
        if service.matches_link(link):
            try:
                return service.generate_embed_code(link)
            except Exception:
                LOG.error("Failed to generate embed code for {0} using {1}".format(link, service))
    return None
