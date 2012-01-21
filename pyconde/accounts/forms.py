# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.template.loader import render_to_string

from userprofiles.forms import RegistrationForm

from .models import Profile, EmailVerification


class ProfileRegistrationForm(RegistrationForm):
    short_info = forms.CharField(widget=forms.Textarea, required=False)

    def save_profile(self, new_user, *args, **kwargs):
        Profile.objects.create(
            user=new_user,
            short_info=self.cleaned_data['short_info']
        )


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(label='Vorname', required=False)
    last_name = forms.CharField(label='Nachname', required=False)

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = [
            'first_name',
            'last_name',
            'short_info',
        ]

    def save(self, *args, **kwargs):
        obj = super(ProfileForm, self).save(*args, **kwargs)
        obj.user.first_name = self.cleaned_data['first_name']
        obj.user.last_name = self.cleaned_data['last_name']
        obj.user.save()

        return obj

    class Meta:
        model = Profile
        include = ('short_info',)


class ChangeEmailForm(forms.Form):
    new_email = forms.EmailField(label='Neue E-Mail-Adresse', required=True)

    def clean_new_email(self):
        new_email = self.cleaned_data['new_email']

        user_emails = User.objects.filter(email=new_email).count()
        verification_emails = EmailVerification.objects.filter(
            new_email=new_email, is_expired=False).count()
        if user_emails + verification_emails > 0:
            raise forms.ValidationError('Diese E-Mail Adresse wird bereits verwendet.')

        return new_email

    def save(self, user=None):
        if not user:
            return None

        verification = EmailVerification.objects.create(
            user=user,
            old_email=user.email,
            new_email=self.cleaned_data['new_email']
        )

        data = {
            'user': user,
            'verification': verification,
            'site': Site.objects.get_current(),
        }

        subject = ''.join(render_to_string(
            'accounts/mails/emailverification_subject.html',
            data
        ).splitlines())
        body = render_to_string(
            'accounts/mails/emailverification.html', data)

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [self.cleaned_data['new_email'],]
        )

        return verification
