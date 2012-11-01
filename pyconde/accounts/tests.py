import unittest
from django.contrib.auth.models import User

from .templatetags import account_tags


class AccountNameFilterTests(unittest.TestCase):
    def test_empty_parameter(self):
        """
        If the parameter given to the filter was empty, we should return just
        None instead of throwing an exception.
        """
        self.assertIsNone(account_tags.account_name(None))
    
    def test_firstname_and_lastname(self):
        """
        Firstname and lastname should be joined with a space.
        """
        user = User(first_name="Test", last_name="User")
        self.assertEquals(u"Test User", account_tags.account_name(user))

    def test_partial_name(self):
        """
        If either the first or the last name of the given user is not set,
        the username should be returned instead. This should also include
        situations where first or last name only consist of whitespaces.
        """
        self.assertEquals(u"username", account_tags.account_name(User(username="username", first_name="Test")))
        self.assertEquals(u"username", account_tags.account_name(User(username="username", last_name="Test")))
        self.assertEquals(u"username", account_tags.account_name(User(username="username")))

        self.assertEquals(u"username", account_tags.account_name(User(username="username", first_name="Test", last_name=" ")))
        self.assertEquals(u"username", account_tags.account_name(User(username="username", first_name=" ", last_name="User")))
