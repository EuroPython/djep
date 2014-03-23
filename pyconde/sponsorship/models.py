import re

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin

from pyconde.conference.models import Conference, CurrentConferenceManager


class SponsorLevel(models.Model):
    conference = models.ForeignKey(Conference, verbose_name=_("conference"))
    name = models.CharField(_("name"), max_length=100)
    order = models.IntegerField(_("order"), default=0)
    description = models.TextField(_("description"), blank=True)
    slug = models.SlugField(_("slug"))

    objects = models.Manager()
    current_conference = CurrentConferenceManager()

    class Meta:
        ordering = ["conference", "order"]
        verbose_name = _("sponsor level")
        verbose_name_plural = _("sponsor levels")

    def __unicode__(self):
        return u"%s %s" % (self.conference, self.name)

    def sponsors(self):
        return self.sponsor_set.filter(active=True).order_by("added")


class Sponsor(models.Model):
    name = models.CharField(_("name"), max_length=100)
    external_url = models.URLField(_("external URL"))
    annotation = models.TextField(_("annotation"), blank=True)
    description = models.TextField(_("description"), blank=True, null=True)
    contact_name = models.CharField(_("contact_name"), max_length=100, blank=True, null=True)
    contact_email = models.EmailField(_(u"Contact e\u2011mail"), blank=True, null=True)
    logo = models.ImageField(_("logo"), upload_to="sponsor_logos/")
    level = models.ForeignKey(SponsorLevel, verbose_name=_("level"))
    added = models.DateTimeField(_("added"), default=now)
    active = models.BooleanField(_("active"), default=False)

    # For some sponsors due to different logo aspect rations we require a way
    # to resize them in a different way on certain positions on the website.
    custom_logo_size_listing = models.CharField(
        _("Custom logo size in listings"), max_length=9, blank=True,
        help_text=_("Format: [width]x[height]. To get the maximum height out "
                    "of a logo, use something like 300x55."),
        null=True)

    @property
    def custom_logo_size_listing_width(self):
        if not self.custom_logo_size_listing:
            return None
        return self.custom_logo_size_listing.split("x")[0]

    @property
    def custom_logo_size_listing_height(self):
        if not self.custom_logo_size_listing:
            return None
        return self.custom_logo_size_listing.split("x")[1]

    def __unicode__(self):
        return self.name

    def clean(self):
        if self.custom_logo_size_listing:
            if not re.match('^\d+x\d+$', self.custom_logo_size_listing):
                raise ValidationError(_("Please specify the custom logo size "
                                        "for listings in the format "
                                        "[width]x[height]."))

    class Meta:
        verbose_name = _("sponsor")
        verbose_name_plural = _("sponsors")


class SponsorListPlugin(CMSPlugin):
    title = models.CharField(_("title"), max_length=100, blank=True)
    levels = models.ManyToManyField(
        'SponsorLevel',
        verbose_name=_("sponsor levels"))
    group = models.BooleanField(_("group by level"), default=False)
    split_list_length = models.IntegerField(
        _("length of split splits"), null=True, blank=True, default=None)
    custom_css_classes = models.CharField(
        _("custom CSS classes"), max_length=100, blank=True,
        help_text=u"Use slides-2rows if your row actually consists of two rows.")

    def copy_relations(self, oldinstance):
        self.levels = oldinstance.levels.all()


class JobOffer(models.Model):
    sponsor = models.ForeignKey(Sponsor, verbose_name=_("sponsor"))
    reply_to = models.EmailField(_("Reply-To"),
        help_text=_('The email address to which responses should be sent.'),
        null=True)
    subject = models.CharField(_("title"), max_length=50)
    text = models.TextField(_("text"))
