import unittest
import datetime

from . import models
from . import utils

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