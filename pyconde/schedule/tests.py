import unittest
from datetime import datetime as dt

from . import utils


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
