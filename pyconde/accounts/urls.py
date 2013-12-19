from django.conf.urls import patterns, url

from . import forms
from . import views


urlpatterns = patterns('django.contrib.auth.views',
        url(r'^login/$', 'login',
            {'template_name': 'userprofiles/login.html',
             'authentication_form': forms.AuthenticationForm},
            name='auth_login'),
        url(r'^password/reset/$', 'password_reset',
            {'template_name': 'userprofiles/password_reset.html',
             'password_reset_form': forms.PasswordResetForm,
             'email_template_name': 'userprofiles/mails/password_reset_email.html'},
            name='auth_password_reset'),
        url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'password_reset_confirm',
            {'template_name': 'userprofiles/password_reset_confirm.html',
             'set_password_form': forms.SetPasswordForm},
            name='auth_password_reset_confirm'),
        url(r'^password/change/$', 'password_change',
            {'template_name': 'userprofiles/password_change.html',
             'password_change_form': forms.PasswordChangeForm},
            name='auth_password_change'),
        url(r'^ajax/users$', views.AutocompleteUser.as_view()),
        url(r'^profile/(?P<uid>\d+)/$', views.ProfileView.as_view(),
            name='account_profile'),
        url(r'^login/request-email/$', views.LoginEmailRequestView.as_view(),
            name='login-email-request'),
        url(r'^email/$', views.EmailChangeView.as_view(),
            name='userprofiles_email_change'),
    )
