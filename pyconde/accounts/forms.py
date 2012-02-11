# -*- coding: utf-8 -*-
from django import forms

from userprofiles.forms import RegistrationForm

from .models import Profile


class ProfileRegistrationForm(RegistrationForm):
    short_info = forms.CharField(widget=forms.Textarea, required=False)

    def save_profile(self, new_user, *args, **kwargs):
        Profile.objects.create(
            user=new_user,
            short_info=self.cleaned_data['short_info']
        )
