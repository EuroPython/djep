# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import ProfileForm, ChangeEmailForm
from .models import EmailVerification


@login_required
def profile_change(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.get_profile())
        if form.is_valid():
            profile = form.save()
            messages.success(request, u'Profil aktualisiert')
            return redirect('accounts_profile_change')
    else:
        form = ProfileForm(instance=request.user.get_profile(), initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name
        })

    return render(request, 'accounts/profile_change.html', {'form': form})


@login_required
def email_change(request):
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST)
        if form.is_valid():
            verification = form.save(request.user)
            return redirect('accounts_email_change_requested')
    else:
        form = ChangeEmailForm()

    return render(request, 'accounts/email_change.html', {'form': form})


@login_required
def email_change_requested(request):
    return render(request, 'accounts/email_change_requested.html', {})


@login_required
def email_change_approve(request, token, code):
    try:
        verification = EmailVerification.objects.get(
            token=token,
            code=code,
            user=request.user,
            is_expired=False
        )
        verification.is_approved = True
        verification.save()
        messages.success(request, u'E-Mail-Adresse geändert in %s' % verification.new_email)
    except EmailVerification.DoesNotExist:
        messages.error(request, u'E-Mail-Adresse kann nicht geändert werden.')

    return redirect('accounts_profile_change')
