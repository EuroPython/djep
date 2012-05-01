from django.conf.urls.defaults import patterns, url

from . import forms
from . import views


urlpatterns = patterns('django.contrib.auth.views',
        url(r'^login/$', 'login', {'template_name': 'userprofiles/login.html', 'authentication_form': forms.AuthenticationForm},
            name='auth_login'),
        url(r'^password/reset/$', 'password_reset',
            {'template_name': 'userprofiles/password_reset.html',
             'password_reset_form': forms.PasswordResetForm,
             'email_template_name': 'userprofiles/mails/password_reset_email.html'},
            name='auth_password_reset'),
        url(r'^password/change/$', 'password_change',
            {'template_name': 'userprofiles/password_change.html',
             'password_change_form': forms.PasswordChangeForm},
            name='auth_password_change'),
        url(r'^ajax/users$', views.AutocompleteUser.as_view()),
    )

