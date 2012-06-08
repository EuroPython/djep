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
from .widgets import AvatarWidget
from ..forms import Submit


class ProfileRegistrationForm(RegistrationForm):
    avatar = forms.ImageField(widget=forms.FileInput, required=False,
        help_text=Profile()._meta.get_field_by_name('avatar')[0].help_text)
    short_info = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(ProfileRegistrationForm, self).__init__(*args, **kwargs)
        account_fields = Fieldset(_('Account data'), Field('username', autofocus="autofocus"), 'password', 'password_repeat')
        profile_fields = Fieldset(_('Profile'), 'first_name', 'last_name', 'email', 'avatar', 'short_info')
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
                account_fields, profile_fields,
                ButtonHolder(Submit('submit', _('Create account'), css_class='btn-primary'))
                )

    def save_profile(self, new_user, *args, **kwargs):
        Profile.objects.create(
            user=new_user,
            avatar=self.cleaned_data['avatar'],
            short_info=self.cleaned_data['short_info']
        )


class AuthenticationForm(auth_forms.AuthenticationForm):
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
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
                Div(Field('email', autofocus="autofocus")),
                ButtonHolder(Submit('reset', _('Reset password'), css_class='btn-primary'))
            )


class PasswordChangeForm(auth_forms.PasswordChangeForm):
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

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
                Div(Field('first_name', autofocus="autofocus"), 'last_name', 'avatar', 'short_info'),
                ButtonHolder(Submit('save', _('Change'), css_class='btn-primary'))
            )

