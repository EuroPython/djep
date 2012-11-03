import unittest
from django.contrib.auth.models import User

from .templatetags import account_tags
from . import forms
from . import models
from . import views


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


class ChangeProfileFormTests(unittest.TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'test', 'test@test.com', 'test')
        self.profile = models.Profile(user=self.user)
        self.profile.save()

    def tearDown(self):
        self.profile.delete()
        self.user.delete()

    def test_change_shortinfo(self):
        """
        If a user provides an updated short info text, it should be saved
        through this form.
        """
        self.assertEquals('', self.profile.short_info)
        form = forms.ProfileForm(instance=self.profile, data={'short_info': 'test'})
        self.assertTrue(form.is_valid())
        new_profile = form.save()
        self.assertEquals('test', new_profile.short_info)


class AutocompleteUserViewTests(unittest.TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'test', 'test@test.com', 'test')
        self.user.first_name = "Firstname"
        self.user.last_name = "Lastname"
        self.user.save()
        self.profile = models.Profile(user=self.user)
        self.profile.save()
        self.view = views.AutocompleteUser()

    def tearDown(self):
        self.profile.delete()
        self.user.delete()

    def test_response_format(self):
        """
        The resulting format should be a list of dicts including the fields
        "label" and "value".
        """
        result = self.view.get_matching_users('Firstname')
        self.assertIn('value', result[0])
        self.assertIn('label', result[0])
        self.assertEquals('Firstname Lastname', result[0]['label'])
        self.assertEquals(self.user.speaker_profile.pk, result[0]['value'])

    def test_firstname_matching(self):
        """
        If the user enters the firstname of a speaker, it should match.
        """
        result = self.view.get_matching_users('Firstname')
        self.assertEquals(1, len(result))
        self.assertEquals('Firstname Lastname', result[0]['label'])

    def test_lastname_matching(self):
        """
        If the user searchs for a speaker by lastname it should also match.
        """
        result = self.view.get_matching_users('Lastname')
        self.assertEquals(1, len(result))
        self.assertEquals('Firstname Lastname', result[0]['label'])

    def test_case_insensitive_search(self):
        """
        The case shouldn't be relevant when searching for a user either
        by first or last name.
        """
        result = self.view.get_matching_users('lastname')
        self.assertEquals(1, len(result))
        self.assertEquals('Firstname Lastname', result[0]['label'])

        result = self.view.get_matching_users('firstname')
        self.assertEquals(1, len(result))
        self.assertEquals('Firstname Lastname', result[0]['label'])
