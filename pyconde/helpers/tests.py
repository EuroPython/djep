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


if __name__ == '__main__':
    unittest.main()
