from django.utils import unittest

from . import utils


class FacetizedUrlTest(unittest.TestCase):
    """
    Note that %3A is a :
    """
    def test_without_q(self):
        res = utils.set_facet_value("http://test.com/", 'test', '123')
        self.assertEquals('http://test.com/?selected_facets=test%3A123', res)

    def test_with_q(self):
        res = utils.set_facet_value("http://test.com/?q=abc", 'test', '123')
        self.assertEquals('http://test.com/?q=abc&selected_facets=test%3A123', res)

    def test_other_facet_exists_with_q(self):
        res = utils.set_facet_value("http://test.com/?q=abc&selected_facets=prev:val", 'test', '123')
        self.assertEquals('http://test.com/?q=abc&selected_facets=prev%3Aval&selected_facets=test%3A123', res)

    def test_other_facet_exists_without_q(self):
        res = utils.set_facet_value("http://test.com/?selected_facets=prev:val", 'test', '123')
        self.assertEquals('http://test.com/?selected_facets=prev%3Aval&selected_facets=test%3A123', res)

    def test_replace_facet(self):
        res = utils.set_facet_value("http://test.com/?selected_facets=prev:val", 'prev', '123')
        self.assertEquals('http://test.com/?selected_facets=prev%3A123', res)


class QsSetterTest(unittest.TestCase):
    def test_set_empty(self):
        self.assertEquals('http://test.com?f=v',
            utils.set_qs_value('http://test.com', [('f', 'v')]))

    def test_set_existing(self):
        self.assertEquals('http://test.com?o=1&f=v',
            utils.set_qs_value('http://test.com?o=1', [('f', 'v')]))

    def test_replace(self):
        self.assertEquals('http://test.com?f=n',
            utils.set_qs_value('http://test.com?f=v', [('f', 'n')]))
