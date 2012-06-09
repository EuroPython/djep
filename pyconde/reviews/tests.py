import unittest
import datetime
from django.test import TestCase, RequestFactory

from . import models
from . import utils
from . import view_mixins

from pyconde.proposals import models as proposal_models


class UtilTests(unittest.TestCase):
    def test_merge_comments_and_versions(self):
        proposal = proposal_models.Proposal()
        c1 = models.Comment(pub_date=datetime.datetime(2000, 1, 1))
        c2 = models.Comment(pub_date=datetime.datetime(2002, 1, 1))
        c3 = models.Comment(pub_date=datetime.datetime(2004, 1, 1))
        v1 = models.ProposalVersion(pub_date=datetime.datetime(2001, 1, 1), original=proposal)
        v2 = models.ProposalVersion(pub_date=datetime.datetime(2003, 1, 1), original=proposal)
        expected = [c1, v1, c2, v2, c3]
        self.assertEquals(expected, utils.merge_comments_and_versions([c1, c2, c3], [v1, v2]))


class OrderMappingMixinTests(TestCase):
    def test_request_order(self):
        req_factory = RequestFactory()
        mixin = view_mixins.OrderMappingMixin()
        mixin.order_mapping = {
            'test': 'mapped_test'
        }

        mixin.default_order = '-test'

        # First let's test some valid orders
        mixin.request = req_factory.get('/?order=test')
        self.assertEquals('test', mixin.get_request_order())
        mixin.request = req_factory.get('/?order=-test')
        self.assertEquals('-test', mixin.get_request_order())

        # Now on to an invalid one that forces a fallback
        # to the default order
        mixin.request = req_factory.get('/?order=lala')
        self.assertEquals('-test', mixin.get_request_order())
