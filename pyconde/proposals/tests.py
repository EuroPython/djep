import datetime
from datetime import timedelta

from django.test import TestCase
from django.forms.models import model_to_dict
from django.contrib.auth import models as auth_models
from django.core.exceptions import ValidationError

from pyconde.conference.test_utils import ConferenceTestingMixin
from pyconde.speakers import models as speakers_models

from . import models
from . import forms
from . import validators


class SubmissionTests(ConferenceTestingMixin, TestCase):
    def setUp(self):
        self.create_test_conference()
        self.user = auth_models.User.objects.create_user(
            'test', 'test@test.com',
            'testpassword')
        speakers_models.Speaker.objects.all().delete()
        self.speaker = speakers_models.Speaker(user=self.user)
        self.speaker.save()

        self.now = datetime.datetime.now()

    def tearDown(self):
        self.destroy_all_test_conferences()

    def test_with_open_sessionkind(self):
        """
        Tests that a proposal can be submitted with an open sessionkind
        """
        proposal = models.Proposal(
            conference=self.conference,
            title="Proposal",
            description="DESCRIPTION",
            abstract="ABSTRACT",
            speaker=self.speaker,
            kind=self.kind,
            audience_level=self.audience_level,
            duration=self.duration,
            track=self.track
        )
        data = model_to_dict(proposal)
        data['agree_to_terms'] = True
        form = forms.ProposalSubmissionForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        now = datetime.datetime.now()
        self.kind.start_date = now - datetime.timedelta(1)
        self.kind.end_date = now + datetime.timedelta(1)
        self.kind.save()

        data = model_to_dict(proposal)
        data['agree_to_terms'] = True
        form = forms.ProposalSubmissionForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_with_closed_sessionkind(self):
        proposal = models.Proposal(
            conference=self.conference,
            title="Proposal",
            description="DESCRIPTION",
            abstract="ABSTRACT",
            speaker=self.speaker,
            kind=self.kind,
            audience_level=self.audience_level,
            duration=self.duration,
            track=self.track
        )
        self.kind.start_date = self.now - timedelta(2)
        self.kind.end_date = self.now - timedelta(1)
        self.kind.closed = None
        self.kind.save()
        form = forms.ProposalSubmissionForm(data=model_to_dict(proposal))
        self.assertFalse(form.is_valid())

        self.kind.start_date = None
        self.kind.end_date = None
        self.kind.closed = True
        self.kind.save()
        form = forms.ProposalSubmissionForm(data=model_to_dict(proposal))
        self.assertFalse(form.is_valid(), form.errors)


class MaxWordsValidatorTests(TestCase):
    def test_too_long(self):
        v = validators.MaxWordsValidator(3)
        self.assertRaises(ValidationError, v, "this is a bit too long")

    def test_ok_with_signs(self):
        v = validators.MaxWordsValidator(3)
        v("hi! hello... world!")

    def test_ok(self):
        v = validators.MaxWordsValidator(2)
        v("hello world!")

    def test_ok_with_whitespaces(self):
        v = validators.MaxWordsValidator(2)
        v("hello    \n   \t world!")


class ListUserProposalsViewTests(ConferenceTestingMixin, TestCase):
    def setUp(self):
        self.create_test_conference('')
        self.create_test_conference('other_')

        self.user = auth_models.User.objects.create_user(
            'test', 'test@test.com',
            'testpassword'
        )
        speakers_models.Speaker.objects.all().delete()
        self.speaker = speakers_models.Speaker(user=self.user)
        self.speaker.save()

        self.now = datetime.datetime.now()

    def tearDown(self):
        self.destroy_all_test_conferences()
        self.user.delete()

    def test_current_conf_only(self):
        """
        This view should only list proposals made for the current conference.
        """
        # In this case the user has made two proposals: One for the current
        # conference, one for another one also managed within the same
        # database. Only the one for the current conference should be listed
        # here.
        previous_proposal = models.Proposal(
            conference=self.other_conference,
            title="Proposal",
            description="DESCRIPTION",
            abstract="ABSTRACT",
            speaker=self.speaker,
            kind=self.other_kind,
            audience_level=self.other_audience_level,
            duration=self.other_duration,
            track=self.other_track
        )
        previous_proposal.save()

        current_proposal = models.Proposal(
            conference=self.conference,
            title="Proposal",
            description="DESCRIPTION",
            abstract="ABSTRACT",
            speaker=self.speaker,
            kind=self.kind,
            audience_level=self.audience_level,
            duration=self.duration,
            track=self.track
        )
        current_proposal.save()

        with self.settings(CONFERENCE_ID=self.conference.pk):
            self.client.login(username=self.user.username,
                              password='testpassword')
            ctx = self.client.get('/proposals/mine/').context
            self.assertEqual([current_proposal], list(ctx['proposals']))

        with self.settings(CONFERENCE_ID=self.other_conference.pk):
            self.client.login(username=self.user.username,
                              password='testpassword')
            ctx = self.client.get('/proposals/mine/').context
            self.assertEqual([previous_proposal], list(ctx['proposals']))

    def test_login_required(self):
        """
        This list should only be available to logged in users.
        """
        self.client.logout()
        self.assertRedirects(
            self.client.get('/proposals/mine/'),
            '/accounts/login/?next=/proposals/mine/')


class SubmitProposalViewTests(TestCase):
    def test_login_required(self):
        self.client.logout()
        self.assertRedirects(
            self.client.get('/proposals/submit/'),
            '/accounts/login/?next=/proposals/submit/')


class SubmitTypedProposalViewTests(TestCase):
    def test_login_required(self):
        self.client.logout()
        self.assertRedirects(
            self.client.get('/proposals/submit/testkind/'),
            '/accounts/login/?next=/proposals/submit/testkind/')


class EditProposalViewTests(TestCase):
    def test_login_required(self):
        self.client.logout()
        self.assertRedirects(
            self.client.get('/proposals/edit/123/'),
            '/accounts/login/?next=/proposals/edit/123/')


class CancelProposalViewTests(TestCase):
    def test_login_required(self):
        self.client.logout()
        self.assertRedirects(
            self.client.get('/proposals/cancel/123/'),
            '/accounts/login/?next=/proposals/cancel/123/')


class LeaveProposalViewTests(TestCase):
    def test_login_required(self):
        self.client.logout()
        self.assertRedirects(
            self.client.get('/proposals/leave/123/'),
            '/accounts/login/?next=/proposals/leave/123/')
