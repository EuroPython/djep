# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.contrib.auth import forms as auth_forms
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from userprofiles.forms import RegistrationForm
from userprofiles.contrib.emailverification.forms import ChangeEmailForm as BaseChangeEmailForm
from userprofiles.contrib.profiles.forms import ProfileForm as BaseProfileForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Fieldset, Div, Field, HTML

from .models import Profile
from . import validators
from .widgets import AvatarWidget
from ..forms import Submit


NUM_ACCOMPANYING_CHILDREN_CHOICES = (
    (0, 0),
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
)


class ProfileRegistrationForm(RegistrationForm):
    """
    Override for the default registration form - adds new fields:

    * Avatar for allowing the user to upload a profile picture
    * and short_info, which allows the user to introduce herself to the
      other attendees/speakers.
    * Organisation name
    * Twitter handle
    * website (URL)
    * Number of accompanying children (dropdown selection)
    * Info about children's ages (free text)

    All these fields are publicly accessible and optional.
    """
    avatar = forms.ImageField(widget=forms.FileInput, required=False,
        help_text=Profile()._meta.get_field_by_name('avatar')[0].help_text)
    short_info = forms.CharField(label=_("short info"), widget=forms.Textarea, required=False)
    organisation = forms.CharField(label=_("Organisation"), required=False)
    twitter = forms.CharField(label=_("Twitter"), required=False)
    website = forms.URLField(label=_("Website"), required=False)
    num_accompanying_children = forms.IntegerField(required=False,
                                                   label=_('Number of accompanying children'),
                                                   widget=forms.Select(choices=NUM_ACCOMPANYING_CHILDREN_CHOICES))
    age_accompanying_children = forms.CharField(
        label=_("Age of accompanying children"), required=False)
    full_name = forms.CharField(required=False)
    display_name = forms.CharField(required=True,
        help_text=_('What name should be displayed to other people?'))
    addressed_as = forms.CharField(label=_("Address me as"), required=False,
        help_text=_('How should we call you in mails and dialogs throughout the website? If you leave this field blank, we will fallback to your display name.'))

    accept_privacy_policy = forms.BooleanField(required=True,
        label=_('I hereby agree to the privacy policy.'))
    accept_pysv_conferences = forms.BooleanField(required=False,
        label=_('I hereby allow the Python Software Verband e.V. to re-use my profile information for upcoming conferences.'))
    accept_ep_conferences = forms.BooleanField(required=False,
        label=_('I hereby allow the EuroPython Society to re-use my profile information for upcoming conferences.'))


    def __init__(self, *args, **kwargs):
        super(ProfileRegistrationForm, self).__init__(*args, **kwargs)
        account_fields = Fieldset(_('Login information'), Field('username', autofocus="autofocus"), 'email', 'password', 'password_repeat')
        profile_fields = Fieldset(_('Personal information'), 'full_name',
                                  'display_name', 'addressed_as',
                                  'avatar', 'short_info')
        profession_fields = Fieldset(_('Professional information'), 'organisation', 'twitter', 'website')
        privacy_fields = Fieldset(_('Privacy Policy'),
            HTML(_('{% load cms_tags %}<p class="control-group">Due to data protection '
                   'regulations you need to explicitly accept our '
                   '<a href="{% page_url "privacy-policy" %}">privacy policy</a>.</p>')),
            'accept_privacy_policy',
            'accept_pysv_conferences',
            'accept_ep_conferences')
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
                account_fields, profile_fields, profession_fields, privacy_fields,
                ButtonHolder(Submit('submit', _('Create account'), css_class='btn btn-primary'))
                )
        if settings.ACCOUNTS_FALLBACK_TO_GRAVATAR:
            self.fields['avatar'].help_text = _("""Please upload an image with a side length of at least 300 pixels.<br />If you don't upload an avatar your Gravatar will be used instead.""")

    def save(self, *args, **kwargs):
        with transaction.commit_on_success():
            super(ProfileRegistrationForm, self).save(*args, **kwargs)

    def save_profile(self, new_user, *args, **kwargs):
        """
        save_profile is used by django-userprofiles as a post-save hook. In this
        case we use it to create a new profile object for the user.
        """
        Profile.objects.create(
            user=new_user,
            avatar=self.cleaned_data['avatar'],
            short_info=self.cleaned_data['short_info'],
            organisation=self.cleaned_data['organisation'],
            twitter=self.cleaned_data['twitter'],
            website=self.cleaned_data['website'],
            num_accompanying_children=self.cleaned_data['num_accompanying_children'] or 0,
            age_accompanying_children=self.cleaned_data['age_accompanying_children'] or '',
            full_name=self.cleaned_data['full_name'],
            display_name=self.cleaned_data['display_name'],
            addressed_as=self.cleaned_data['addressed_as'],
            accept_pysv_conferences=self.cleaned_data['accept_pysv_conferences'],
            accept_ep_conferences=self.cleaned_data['accept_ep_conferences']
        )

    def clean_twitter(self):
        """
        Allow the user to enter either "@foo" or "foo" as their twitter handle.
        """
        value = self.cleaned_data.get('twitter', '')
        value = value.lstrip('@')
        validators.twitter_username(value)  # validates the max_length
        return value


class AuthenticationForm(auth_forms.AuthenticationForm):
    """
    Override for the default login/authentication form that acts as entrypoint
    for crispy_forms.

    Note that right now it includes some hardcoded strings.
    """
    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
                Div(Field('username', autofocus="autofocus"), 'password'),
                ButtonHolder(
                    HTML(ugettext(u'<ul><li><a href="%(register_url)s">Don\'t have an account yet?</a></li><li><a href="%(password_reset_url)s">Forgot your password?</a></li></ul>') % {
                        'register_url': reverse('userprofiles_registration'), 
                        'password_reset_url': reverse('auth_password_reset')
                    }),
                    Submit('login', _('Log in'), css_class='btn btn-primary')
                )
            )


class PasswordResetForm(auth_forms.PasswordResetForm):
    """
    Override for the default password reset form which acts as entrypoint
    for crispy forms.
    """
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
                Div(Field('email', autofocus="autofocus")),
                ButtonHolder(Submit('reset', _('Reset password'), css_class='btn-primary'))
            )


class SetPasswordForm(auth_forms.SetPasswordForm):
    """
    Override for the default password reset form which acts as entrypoint
    for crispy forms.
    """
    def __init__(self, *args, **kwargs):
        super(SetPasswordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
                Div(Field('new_password1', autofocus="autofocus"), 'new_password2'),
                ButtonHolder(Submit('reset', _('Set password'), css_class='btn-primary'))
            )


class PasswordChangeForm(auth_forms.PasswordChangeForm):
    """
    Override for the default password change form which acts as entrypoint
    for crispy forms.
    """
    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
                Div(Field('old_password', autofocus="autofocus"), 'new_password1', 'new_password2'),
                ButtonHolder(Submit('save', _('Change password'), css_class='btn-primary'))
            )


class ProfileForm(BaseProfileForm):
    avatar_size = (settings.THUMBNAIL_SIZE, settings.THUMBNAIL_SIZE)
    avatar_help_text = Profile()._meta.get_field_by_name('avatar')[0].help_text
    avatar = forms.ImageField(widget=AvatarWidget(size=avatar_size),
        required=False, help_text=avatar_help_text)
    organisation = forms.CharField(label=_("organisation"), required=False)
    num_accompanying_children = forms.IntegerField(required=False,
                                                   label=_('Number of accompanying children'),
                                                   widget=forms.Select(choices=NUM_ACCOMPANYING_CHILDREN_CHOICES))
    age_accompanying_children = forms.CharField(label=_("Age of accompanying children"),
                                                required=False)

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        profile_fields = Fieldset(_('Personal information'), 'full_name',
                                  'display_name', 'addressed_as',
                                  'avatar', 'short_info')
        profession_fields = Fieldset(_('Professional information'), 'organisation', 'twitter', 'website')
        privacy_fields = Fieldset(
            _('Privacy Policy'),
            'accept_pysv_conferences',
            'accept_ep_conferences')
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            profile_fields, profession_fields, privacy_fields,
            (Div(Field('num_accompanying_children', disabled=True),
                 Field('age_accompanying_children', disabled=True))
             if settings.CHILDREN_DATA_DISABLED else
             Div(Field('num_accompanying_children'),
                 Field('age_accompanying_children'))),
            ButtonHolder(Submit('save', _('Change'), css_class='btn-primary'))
        )
        if settings.ACCOUNTS_FALLBACK_TO_GRAVATAR:
            self.fields['avatar'].help_text = _("""Please upload an image with a side length of at least 300 pixels.<br />If you don't upload an avatar your Gravatar will be used instead.""")
        # children fields - may be disabled on registration form (see above)
        # and removed completely from profile form
        if settings.CHILDREN_DATA_DISABLED:
            del self.fields['num_accompanying_children']
            del self.fields['age_accompanying_children']

    def clean_accept_pysv_conferences(self):
        value = self.cleaned_data['accept_pysv_conferences']
        if not value and self.instance.accept_pysv_conferences:
            self.data['accept_pysv_conferences'] = True
            raise ValidationError(_("You previously agreed to this option"
                                    " which can no longer be revoked."))
        return value

    def clean_accept_ep_conferences(self):
        value = self.cleaned_data['accept_ep_conferences']
        if not value and self.instance.accept_ep_conferences:
            self.data['accept_ep_conferences'] = True
            raise ValidationError(_("You previously agreed to this option"
                                    " which can no longer be revoked."))
        return value


class LoginEmailRequestForm(forms.Form):
    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super(LoginEmailRequestForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            'email',
            ButtonHolder(Submit('save', _("Continue"), css_class='btn btn-primary')))


class ChangeEmailForm(BaseChangeEmailForm):

    def __init__(self, *args, **kwargs):
        super(ChangeEmailForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            'new_email',
            ButtonHolder(Submit('save', _("Change e-mail address"), css_class='btn btn-primary')))
