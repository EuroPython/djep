from __future__ import print_function

from django import template
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase, TransactionTestCase

from .templatetags import account_tags
from . import forms
from . import models
from . import views
from . import validators


class DisplayNameFilterTests(TransactionTestCase):
    def test_empty_parameter(self):
        self.assertIsNone(account_tags.display_name(None))

    def test_display_name_given(self):
        """
        If the user has specified a display name, it should be returned here.
        """
        user = User(username="username")
        user.save()
        profile = models.Profile(display_name="Display Name", user=user)
        self.assertEquals("Display Name", account_tags.display_name(user))

    def test_no_display_name_given(self):
        """
        If the user has not specified a display name, fallback to the
        userername.
        """
        user = User(username="username")
        user.save()
        profile = models.Profile(display_name="", user=user)
        profile.save()
        self.assertEquals("username", account_tags.display_name(user))


class AddressedAsFilterTests(TransactionTestCase):
    def test_empty_parameter(self):
        self.assertIsNone(account_tags.addressed_as(None))

    def test_addressed_as_given(self):
        user = User(username="username")
        user.save()
        profile = models.Profile(display_name="Display Name",
            addressed_as="Addressed as", user=user)
        self.assertEquals("Addressed as", account_tags.addressed_as(user))

    def test_no_addressed_as_given(self):
        user = User(username="username")
        user.save()
        profile = models.Profile(addressed_as="", display_name="Display name", user=user)
        profile.save()
        self.assertEquals("Display name", account_tags.addressed_as(user))


class AvatarTagTests(TransactionTestCase):
    def test_no_user(self):
        """
        If you pass in a None object as user, a ValueError is expected.
        """
        tmpl = template.Template(
            '''{% load account_tags %}{% avatar user %}''')
        with self.assertRaises(ValueError):
            tmpl.render(template.Context({'user': None}))

    def test_with_user_without_avatar(self):
        expected = '''<img class="avatar gravatar" src="images/noavatar80.png" alt="" style="width: 80px; height: 80px"/>'''
        user = User.objects.create_user('testuser', 'test@test.com',
            password='test')
        profile = models.Profile(user=user)
        profile.save()
        with self.settings(ACCOUNTS_FALLBACK_TO_GRAVATAR=False):
            tmpl = template.Template(
                '''{% load account_tags %}{% avatar user %}''')
            self.assertEquals(expected,
                tmpl.render(template.Context({'user': user})).lstrip().rstrip())

    def test_with_profile_without_avatar(self):
        expected = '''<img class="avatar gravatar" src="images/noavatar80.png" alt="" style="width: 80px; height: 80px"/>'''
        user = User.objects.create_user('testuser', 'test@test.com',
            password='test')
        profile = models.Profile(user=user)
        profile.save()
        with self.settings(ACCOUNTS_FALLBACK_TO_GRAVATAR=False):
            tmpl = template.Template(
                '''{% load account_tags %}{% avatar user %}''')
            self.assertEquals(expected,
                tmpl.render(template.Context({'user': profile})).lstrip().rstrip())


class ChangeProfileFormTests(TestCase):
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


class AutocompleteUserViewTests(TestCase):
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


class TwitterUsernameValidatorTest(TestCase):
    def test_start_with_at(self):
        with self.assertRaises(ValidationError):
            validators.twitter_username("@test")

    def test_too_long(self):
        with self.assertRaises(ValidationError):
            validators.twitter_username("test test test t")


class ProfileRegistrationFormTests(TestCase):
    def _required_data(self, **kwargs):
        """
        Build a dict of required data for the ProfileRegistrationForm and
        update it with the given kwargs.
        """
        required = {
            'username': 'foo',
            'password': 'foo',
            'password_repeat': 'foo',
            'display_name': 'foo',
            'email': 'foo@example.com',
            'accept_privacy_policy': '1',
        }
        required.update(kwargs)
        return required

    def test_twitter_handle_leading_at(self):
        data = self._required_data(twitter='@foo')
        f = forms.ProfileRegistrationForm(data)
        self.assertTrue(f.is_valid())
        self.assertEqual(f.cleaned_data['twitter'], 'foo')

    def test_twitter_handle_too_long(self):
        handle = 16 * 'a'
        data = self._required_data(twitter=handle)
        f = forms.ProfileRegistrationForm(data)
        self.assertFalse(f.is_valid())
        errors = f['twitter'].errors
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0], 'Twitter usernames have only 15 characters or less')

    def test_twitter_handle_15_chars_with_leading_at(self):
        handle = '@' + 15 * 'a'
        data = self._required_data(twitter=handle)
        f = forms.ProfileRegistrationForm(data)
        self.assertTrue(f.is_valid())
