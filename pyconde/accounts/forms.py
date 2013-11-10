# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth import forms as auth_forms
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

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
    * Organisation name
    * Twitter handle
    * website (URL)
    * Number of accompanying children (dropdown selection)
    * Info about children's ages (free text)

    All these fields are publicly accessible and optional.
    """
    avatar = forms.ImageField(widget=forms.FileInput, required=False,
        help_text=Profile()._meta.get_field_by_name('avatar')[0].help_text)
    short_info = forms.CharField(_("short info"), widget=forms.Textarea, required=False)
    organisation = forms.CharField(label=_("organisation"), required=False)
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
        account_fields = Fieldset(_('Login information'), Field('username', autofocus="autofocus"), 'email', 'password', 'password_repeat')
        profile_fields = Fieldset(_('Personal information'), 'first_name', 'last_name', 'gender',
                                  'avatar', 'short_info')
        profession_fields = Fieldset(_('Professional information'), 'organisation', 'twitter', 'website')
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
                account_fields, profile_fields, profession_fields,
                ButtonHolder(Submit('submit', _('Create account'), css_class='btn btn-primary'))
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
            organisation=self.cleaned_data['organisation'],
            num_accompanying_children=self.cleaned_data['num_accompanying_children'] or 0,
            age_accompanying_children=self.cleaned_data['age_accompanying_children'] or ''
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
                    HTML(ugettext(u'<ul><li><a href="%(register_url)s">Don\'t have an account yet?</a></li><li><a href="%(password_reset_url)s">Forgot your password?</a></li></ul>') % {
                        'register_url': reverse('userprofiles_registration'), 
                        'password_reset_url': reverse('auth_password_reset')
                    }),
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
    organisation = forms.CharField(label=_("organisation"), required=False)
    num_accompanying_children = forms.IntegerField(required=False,
                                                   label=_('Number of accompanying children'),
                                                   widget=forms.Select(choices=NUM_ACCOMPANYING_CHILDREN_CHOICES))
    age_accompanying_children = forms.CharField(label=_("Age of accompanying children"),
                                                required=False)

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Div(Field('first_name', autofocus="autofocus"), 'last_name',
                'avatar', 'short_info', 'organisation', 'twitter', 'website'),
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

class LoginEmailRequestForm(forms.Form):
    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super(LoginEmailRequestForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            'email',
            ButtonHolder(Submit('save', _("Continue"), css_class='btn-primary')))
