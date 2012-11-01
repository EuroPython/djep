import unittest
from datetime import datetime as dt
import logging

from . import utils
from . import slides
from . import videos


logging.disable(logging.CRITICAL)


class MockEvent(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end


class ScheduleGeneratorTests(unittest.TestCase):
    def test_number_of_rows_in_order(self):
        evts = [
            MockEvent(dt(2012, 6, 1, 10, 00), dt(2012, 6, 1, 10, 30)),
            MockEvent(dt(2012, 6, 1, 10, 30), dt(2012, 6, 1, 11, 00)),
            MockEvent(dt(2012, 6, 1, 11, 00), dt(2012, 6, 1, 11, 30)),
        ]
        self.assertEquals(3, utils._get_number_of_rows(evts, 30))

    def test_number_of_rows_in_parallel(self):
        evts = [
            MockEvent(dt(2012, 6, 1, 10, 00), dt(2012, 6, 1, 10, 30)),
            MockEvent(dt(2012, 6, 1, 10, 30), dt(2012, 6, 1, 11, 00)),
            MockEvent(dt(2012, 6, 1, 10, 30), dt(2012, 6, 1, 11, 00)),
            MockEvent(dt(2012, 6, 1, 11, 00), dt(2012, 6, 1, 11, 30)),
        ]
        self.assertEquals(3, utils._get_number_of_rows(evts, 30))

    def test_number_of_rows_out_of_order(self):
        evts = [
            MockEvent(dt(2012, 6, 1, 11, 00), dt(2012, 6, 1, 11, 30)),
            MockEvent(dt(2012, 6, 1, 10, 00), dt(2012, 6, 1, 10, 30)),
            MockEvent(dt(2012, 6, 1, 10, 30), dt(2012, 6, 1, 11, 00)),
            MockEvent(dt(2012, 6, 1, 10, 30), dt(2012, 6, 1, 11, 00)),
        ]
        self.assertEquals(3, utils._get_number_of_rows(evts, 30))

    def test_base_grid_creation(self):
        start = dt(2012, 6, 1, 9, 0)
        end = dt(2012, 6, 1, 10, 30)
        self.assertEquals(3, len(utils._create_base_grid(start, end, 30)))

    def test_strip_rows(self):
        e1 = utils.GridCell(None, 2)
        e1.end = dt(2012, 6, 1, 10, 30)
        rows = [
            utils.GridRow(dt(2012, 6, 1, 9, 0), dt(2012, 6, 1, 9, 30), []),
            utils.GridRow(dt(2012, 6, 1, 9, 30), dt(2012, 6, 1, 10, 0), [e1]),
            utils.GridRow(dt(2012, 6, 1, 10, 0), dt(2012, 6, 1, 10, 30), []),
            utils.GridRow(dt(2012, 6, 1, 10, 30), dt(2012, 6, 1, 11, 00), []),
        ]
        result = utils._strip_empty_rows(rows)
        self.assertEquals(2, len(result))
        self.assertEquals(rows[1:3], result)

    def test_strip_rows_empty(self):
        rows = [
            utils.GridRow(dt(2012, 6, 1, 9, 0), dt(2012, 6, 1, 9, 30), []),
            utils.GridRow(dt(2012, 6, 1, 9, 30), dt(2012, 6, 1, 10, 0), []),
            utils.GridRow(dt(2012, 6, 1, 10, 0), dt(2012, 6, 1, 10, 30), []),
            utils.GridRow(dt(2012, 6, 1, 10, 30), dt(2012, 6, 1, 11, 00), []),
        ]
        result = utils._strip_empty_rows(rows)
        self.assertEquals(0, len(result))


class SlideCodeGeneratorTests(unittest.TestCase):
    def test_prezi_match(self):
        service = slides.PreziService()
        self.assertTrue(service.matches_link('http://prezi.com/mkg9y_pl1cxd/presentation-on-presentations/'))
        self.assertFalse(service.matches_link("https://speakerdeck.com/u/speakerdeck/p/introduction-to-speakerdeck"))

    def test_prezi_id_extraction(self):
        service = slides.PreziService()
        self.assertEquals('mkg9y_pl1cxd', service.extract_id('http://prezi.com/mkg9y_pl1cxd/presentation-on-presentations/'))

    def test_slideshare_match(self):
        service = slides.SlideShareService()
        self.assertTrue(service.matches_link('http://www.slideshare.net/zeeg/pycon-2011-scaling-disqus-7251315'))
        assert not service.matches_link("https://speakerdeck.com/u/speakerdeck/p/introduction-to-speakerdeck")

    def test_speakerdeck_match(self):
        service = slides.SpeakerDeckService()
        self.assertTrue(service.matches_link("https://speakerdeck.com/u/speakerdeck/p/introduction-to-speakerdeck"))
        self.assertTrue(service.matches_link("http://speakerdeck.com/u/speakerdeck/p/introduction-to-speakerdeck"))
        self.assertFalse(service.matches_link("http://youtube.com"))

    def test_speakerdeck_generation(self):
        doc = SAMPLE_SPEAKERDECK_DOC
        code = slides.SpeakerDeckService().generate_embed_code(None, doc=doc)
        self.assertEquals("""<script async class="speakerdeck-embed" data-id="123" data-ratio="1.3333333333333333" src="//speakerdeck.com/assets/embed.js"></script>""",
            code)

    def test_slideshare_oembed_link(self):
        service = slides.SlideShareService()
        self.assertTrue(service.get_oembed_url('http://www.slideshare.net/zeeg/pycon-2011-scaling-disqus-7251315') == 'http://www.slideshare.net/api/oembed/2?format=json&url=http%3A%2F%2Fwww.slideshare.net%2Fzeeg%2Fpycon-2011-scaling-disqus-7251315')


class VideoServiceTests(unittest.TestCase):
    def test_youtube_oembed_link(self):
        """
        Internal test to make sure that the url generator for youtube works.
        """
        service = videos.YouTubeService()
        self.assertEquals(
            r"http://www.youtube.com/oembed?url=http%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DcR2XilcGYOo&format=json",
            service.generate_oembed_url('http://www.youtube.com/watch?v=cR2XilcGYOo')
            )


SAMPLE_SPEAKERDECK_DOC = """<!DOCTYPE html>
<html>
<body class="signed-out">
  <div id="content">

<section id="presentation" class="feature">
  <div class="wrapper">
    <div class="main">
      <h1>Introduction to Speakerdeck</h1>
        <div class="slide_frame" id="slides_container">
          <div class="speakerdeck-embed"
            data-id="123"
            data-ratio="1.3333333333333333"
            data-slide=""></div>
        </div>
    </div>
  </div>
</section>

  </div>


</body>
</html>
"""
