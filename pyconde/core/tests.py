from django.test import TestCase

from .management.commands.optimize_media_images import is_thumbnail
from .templatetags import core_tags


class OptimizeMediaImagesTests(TestCase):
    def test_thumbnail_detection(self):
        self.assertTrue(is_thumbnail('quote-2.png.100x100_q85.jpg'))
        self.assertTrue(is_thumbnail('quote-2.png.100x100_q85.png'))
        self.assertTrue(is_thumbnail('image.jpg.112x44_q85_crop.jpg'))
        self.assertTrue(is_thumbnail('image.jpg.112x44_q85_crop.png'))


class DomainFilterTests(TestCase):
    def test_valid_url(self):
        self.assertEquals("domain.com", core_tags.domain("http://domain.com/path"))

    def test_invalid_url(self):
        self.assertEquals("invalid", core_tags.domain("invalid"))
