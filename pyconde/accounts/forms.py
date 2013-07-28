# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth import forms as auth_forms
from django.utils.translation import ugettext_lazy as _

from userprofiles.forms import RegistrationForm
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
    * Twitter handle
    * website (URL)
    * Number of accompanying children (dropdown selection)
    * Info about children's ages (free text)

    All these fields are publicly accessible and optional.
    """
    avatar = forms.ImageField(widget=forms.FileInput, required=False,
        help_text=Profile()._meta.get_field_by_name('avatar')[0].help_text)
    short_info = forms.CharField(_("short info"), widget=forms.Textarea, required=False)
    twitter = forms.CharField(_("Twitter"), required=False,
        validators=[validators.twitter_username])
    website = forms.URLField(_("Website"), required=False)
    num_accompanying_children = forms.IntegerField(required=False,
                                                   label=_('Number of accompanying children'),
                                                   widget=forms.Select(choices=NUM_ACCOMPANYING_CHILDREN_CHOICES))
    age_accompanying_children = forms.CharField(
        label=_("Age of accompanying children"), required=False)

    def __init__(self, *args, **kwargs):
        super(ProfileRegistrationForm, self).__init__(*args, **kwargs)
        account_fields = Fieldset(_('Account data'), Field('username', autofocus="autofocus"), 'email', 'password', 'password_repeat')
        profile_fields = Fieldset(_('Profile'), 'first_name', 'last_name',
                                  'avatar', 'short_info', 'twitter', 'website',
                                  'num_accompanying_children',
                                  'age_accompanying_children')
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
                account_fields, profile_fields,
                ButtonHolder(Submit('submit', _('Create account'), css_class='btn-primary'))
                )
        if settings.ACCOUNTS_FALLBACK_TO_GRAVATAR:
            self.fields['avatar'].help_text = _("""Please upload an image with a side length of at least 300 pixels.<br />If you don't upload an avatar your Gravatar will be used instead.""")

    def save_profile(self, new_user, *args, **kwargs):
        """
        save_profile is used by django-userprofiles as a post-save hook. In this
        case we use it to create a new profile object for the user.
        """
        Profile.objects.create(
            user=new_user,
            avatar=self.cleaned_data['avatar'],
            short_info=self.cleaned_data['short_info'],
            num_accompanying_children=self.cleaned_data['num_accompanying_children'],
            age_accompanying_children=self.cleaned_data['age_accompanying_children']
        )


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
                    HTML('<ul><li><a href="{0}">Noch kein Konto?</a></li><li><a href="{1}">Passwort vergessen?</a></li></ul>'.format(
                        reverse('userprofiles_registration'), reverse('auth_password_reset'))),
                    Submit('login', _('Log in'), css_class='btn-primary')
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
    num_accompanying_children = forms.IntegerField(required=False,
                                                   label=_('Number of accompanying children'),
                                                   widget=forms.Select(choices=NUM_ACCOMPANYING_CHILDREN_CHOICES))

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Div(Field('first_name', autofocus="autofocus"), 'last_name',
                'avatar', 'short_info', 'twitter', 'website',
                'num_accompanying_children'),
            ButtonHolder(Submit('save', _('Change'), css_class='btn-primary'))
        )
        if settings.ACCOUNTS_FALLBACK_TO_GRAVATAR:
            self.fields['avatar'].help_text = _("""Please upload an image with a side length of at least 300 pixels.<br />If you don't upload an avatar your Gravatar will be used instead.""")


class LoginEmailRequestForm(forms.Form):
    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super(LoginEmailRequestForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            'email',
            ButtonHolder(Submit('save', _("Continue"), css_class='btn-primary')))
