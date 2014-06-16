import unittest

from .templatetags import helper_tags


class ShyFilterTests(unittest.TestCase):
    def test_word_split(self):
        t = u"Hallo Welt, das ist einlangeswort"
        r = u"Hallo Welt, das ist einlan&shy;geswor&shy;t"

        self.assertEquals(r, helper_tags.shy(t, 6))

        t = u"ein ontologiebasiertes Forschungsinformationssystem"
        r = u"ein ontologiebasier&shy;tes Forschungsinfor&shy;mationssystem"

        self.assertEquals(r, helper_tags.shy(t, 15))


class DomainFilterTests(unittest.TestCase):
    def test_valid_url(self):
        self.assertEquals("domain.com", helper_tags.domain("http://domain.com/path"))

    def test_invalid_url(self):
        self.assertEquals("invalid", helper_tags.domain("invalid"))


if __name__ == '__main__':
    unittest.main()
