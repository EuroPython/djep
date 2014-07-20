# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.contrib.markup.templatetags.markup import markdown
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.db import models
from django.db.models import Q

from cms.models import CMSPlugin

from easy_thumbnails.fields import ThumbnailerImageField
from taggit.managers import TaggableManager
from validatorchain import ValidatorChain

from . import validators


avatar_min_max_dimension = {}
if validators.AVATAR_MIN_DIMENSION:
    avatar_min_max_dimension.update({
        'min_w': validators.AVATAR_MIN_DIMENSION[0],
        'min_h': validators.AVATAR_MIN_DIMENSION[1]
    })
    if validators.AVATAR_MAX_DIMENSION:
        avatar_help_text = _('Please upload an image with a side length between %(min_w)dx%(min_h)d px and %(max_w)dx%(max_h)d px.')
        avatar_min_max_dimension.update({
            'max_w': validators.AVATAR_MAX_DIMENSION[0],
            'max_h': validators.AVATAR_MAX_DIMENSION[1]
        })
    else:
        avatar_help_text = _('Please upload an image with a side length of at least %(min_w)dx%(min_h)d px.')
else:
    if validators.AVATAR_MAX_DIMENSION:
        avatar_help_text = _('Please upload an image with a side length of at most %(max_w)dx%(max_h)d px.')
        avatar_min_max_dimension.update({
            'max_w': validators.AVATAR_MAX_DIMENSION[0],
            'max_h': validators.AVATAR_MAX_DIMENSION[1]
        })
    else:
        avatar_help_text = ''
avatar_help_text = avatar_help_text % avatar_min_max_dimension


class BadgeStatus(models.Model):
    name = models.CharField(_('Name'), max_length=50)
    slug = models.SlugField(_('slug'), max_length=50)

    class Meta:
        ordering = ('name',)
        verbose_name = _('Status')
        verbose_name_plural = _('Statuses')

    def __unicode__(self):
        return self.name


class Profile(models.Model):
    """
    A userprofile model that provides a short_info, twitter handle, website URL, avatar
    field and details about number/age of accompanying children

    This is also used as AUTH_PROFILE_MODULE.
    """
    user = models.OneToOneField(User, related_name='profile')
    short_info = models.TextField(_('short info'), blank=True)
    avatar = ThumbnailerImageField(
        _('avatar'), upload_to='avatars', null=True, blank=True,
        help_text=avatar_help_text,
        validators=ValidatorChain().add(validators.avatar_dimension)
                                   .add(validators.avatar_format, skip_on_error=True)
    )
    num_accompanying_children = models.PositiveIntegerField(_('Number of accompanying children'),
        null=True, blank=True, default=0)
    age_accompanying_children = models.CharField(_("Age of accompanying children"), blank=True, max_length=20)
    twitter = models.CharField(_("Twitter"), blank=True, max_length=20,
        validators=[validators.twitter_username])
    website = models.URLField(_("Website"), blank=True)
    organisation = models.TextField(_('Organisation'), blank=True)
    full_name = models.CharField(_("Full name"), max_length=255, blank=True)
    display_name = models.CharField(_("Display name"), max_length=255,
        help_text=_('What name should be displayed to other people?'),
        blank=True)
    addressed_as = models.CharField(_("Address me as"), max_length=255,
        help_text=_('How should we call you in mails and dialogs throughout the website?'),
        blank=True)
    accept_pysv_conferences = models.BooleanField(_('Allow copying to PySV conferences'),
        default=False, blank=True)
    accept_ep_conferences = models.BooleanField(_('Allow copying to EPS conferences'),
        default=False, blank=True)
    accept_job_offers = models.BooleanField(_('Allow sponsors to send job offers'),
        default=False, blank=True)

    badge_status = models.ManyToManyField('accounts.BadgeStatus', blank=True,
        verbose_name=_('Badge status'), related_name='profiles')

    sessions_attending = models.ManyToManyField('schedule.Session', blank=True,
        related_name='attendees', verbose_name=_('Trainings'),
        limit_choices_to=Q(kind__slug__in=settings.SCHEDULE_ATTENDING_POSSIBLE))

    tags = TaggableManager(blank=True)

    class Meta:
        permissions = (
            ('send_user_mails', _('Allow sending mails to users through the website')),
            ('export_guidebook', _('Allow export of guidebook data')),
            ('see_checkin_info', _('Allow seeing check-in information')),
            ('perform_purchase', _('Allow performing purchases'))
        )

    @cached_property
    def short_info_rendered(self):
        return markdown(self.short_info, 'safe')


class UserListPlugin(CMSPlugin):

    badge_status = models.ManyToManyField('BadgeStatus', blank=True,
        verbose_name=_('Status'))
    additional_names = models.TextField(_('Additional names'), blank=True,
        default='', help_text=_('Users without account. One name per line.'))

    def copy_relations(self, oldinstance):
        self.badge_status = oldinstance.badge_status.all()

    @property
    def additional_names_list(self):
        return list(set(bs for bs in self.additional_names.split('\n') if bs))


@receiver(user_logged_in)
def show_logged_in_message(request, user, **kwargs):
    messages.success(request, _("You've logged in successfully."),
                     fail_silently=True)
