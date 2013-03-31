import datetime

from django.db import models
from django.db.models import Q
from django import forms
from django.utils.translation import ugettext_lazy as _

from timezones.fields import TimeZoneField

from pyconde import south_rules


CONFERENCE_CACHE = {}


class Conference(models.Model):
    """
    the full conference for a specific year, e.g. US PyCon 2012.
    """

    title = models.CharField(_("title"), max_length=100)

    # when the conference runs
    start_date = models.DateField(_("start date"), null=True, blank=True)
    end_date = models.DateField(_("end date"), null=True, blank=True)

    # timezone the conference is in
    timezone = TimeZoneField(_("timezone"), blank=True)

    reviews_start_date = models.DateTimeField(null=True, blank=True)
    reviews_end_date = models.DateTimeField(null=True, blank=True)
    reviews_active = models.NullBooleanField()

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        super(Conference, self).save(*args, **kwargs)
        if self.id in CONFERENCE_CACHE:
            del CONFERENCE_CACHE[self.id]

    def delete(self):
        pk = self.pk
        super(Conference, self).delete()
        try:
            del CONFERENCE_CACHE[pk]
        except KeyError:
            pass

    def get_reviews_active(self):
        if self.reviews_active is not None:
            return self.reviews_active
        now = datetime.datetime.now()
        if self.reviews_start_date and self.reviews_end_date:
            return self.reviews_start_date <= now <= self.reviews_end_date
        return False

    class Meta(object):
        verbose_name = _("conference")
        verbose_name_plural = _("conferences")


class CurrentConferenceManager(models.Manager):
    """
    A simple filter that filters instances of the current class by the
    foreign key "conference" being the current conference.
    """
    def get_query_set(self):
        return super(CurrentConferenceManager, self).get_query_set().filter(conference=current_conference())


class Section(models.Model):
    """
    a section of the conference such as "Tutorials", "Workshops",
    "Talks", "Expo", "Sprints", that may have its own review and
    scheduling process.
    """

    conference = models.ForeignKey(Conference, verbose_name=_("conference"),
        related_name='sections')

    name = models.CharField(_("name"), max_length=100)

    # when the section runs
    start_date = models.DateField(_("start date"), null=True, blank=True)
    end_date = models.DateField(_("end date"), null=True, blank=True)

    slug = models.SlugField(_("slug"), null=True, blank=True)
    order = models.IntegerField(_("order"), default=0)

    description = models.TextField(_("description"), blank=True, null=True)

    objects = models.Manager()
    current_objects = CurrentConferenceManager()

    def __unicode__(self):
        return self.name

    class Meta(object):
        verbose_name = _("section")
        verbose_name_plural = _("sections")


class AudienceLevel(models.Model):
    """
    Sessions, presentations and so on have all a particular target audience.
    Within this target audience you usually have certain levels of experience
    with the topic.

    Most of the there are 3 levels:

    * Novice
    * Intermediate
    * Experienced

    That said, there are sometimes talks that go beyond this by being for
    instance targeted at only people with "Core Contributor" expierence.

    To make custom styling of these levels a bit more flexible, the audience
    level also comes with a slug field for use as CSS-class, while the level
    property is used to sort the audience level.
    """
    conference = models.ForeignKey(Conference, verbose_name=_("conference"))
    name = models.CharField(_("name"), max_length=100)
    slug = models.SlugField(_("slug"))
    level = models.IntegerField(_("level"), blank=True, null=True)

    objects = models.Manager()
    current_objects = CurrentConferenceManager()

    class Meta(object):
        verbose_name = _("audience level")
        verbose_name_plural = _("audience levels")

    def __unicode__(self):
        return self.name


class SessionDuration(models.Model):
    """
    A conference has usually two kinds of session slot durations. One for
    short talks and one for longer talks. The actual time span varies. Some
    conferences have 20 minutes and 50 minutes respectively, some 15 and 30
    minutes for each session.
    """
    conference = models.ForeignKey(Conference, verbose_name=_("conference"))
    label = models.CharField(_("label"), max_length=100)
    slug = models.SlugField(_("slug"))
    minutes = models.IntegerField(_("minutes"))

    objects = models.Manager()
    current_objects = CurrentConferenceManager()

    class Meta(object):
        verbose_name = _("session duration")
        verbose_name_plural = _("session durations")

    def __unicode__(self):
        return u"%s (%d min.)" % (self.label, self.minutes)


class ActiveSessionKindManager(CurrentConferenceManager):
    def filter_open_kinds(self):
        now = datetime.datetime.utcnow()
        return self.get_query_set().filter(
            Q(closed=False)
            | Q(Q(closed=None) & Q(start_date__lt=now) & Q(end_date__gte=now))
            )


class SessionKind(models.Model):
    conference = models.ForeignKey(Conference, verbose_name=_("conference"))
    name = models.CharField(_("name"), max_length=50)
    slug = models.SlugField(_("slug"))
    closed = models.NullBooleanField()
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    # TODO: available_durations = models.ManyToManyField('SessionDuration', blank=True, null=True)
    # TODO: available_tracks = models.ManyToManyField('Track', blank=True, null=True)

    objects = models.Manager()
    current_objects = ActiveSessionKindManager()

    class Meta(object):
        verbose_name = _("session kind")
        verbose_name_plural = _("session kinds")

    def __unicode__(self):
        return self.name

    def clean(self):
        """
        A SessionKind can either have neither start nor end date or both.
        """
        super(SessionKind, self).clean()
        if self.closed is None:
            if self.start_date is None or self.end_date is None:
                raise forms.ValidationError(_("You have to specify a start and end date if you leave the 'closed' status undetermined"))
            if self.start_date >= self.end_date:
                raise forms.ValidationError(_("The end date has to be after the start date"))

    def accepts_proposals(self):
        if self.conference.get_reviews_active():
            return False
        now = datetime.datetime.utcnow()
        if self.conference.start_date is not None:
            if self.conference.start_date < now.date():
                return False
        if self.closed is None:
            return self.start_date <= now <= self.end_date
        return not self.closed


class Track(models.Model):
    conference = models.ForeignKey(Conference, verbose_name=_("conference"))
    name = models.CharField(_("name"), max_length=100)
    slug = models.SlugField(_("slug"))
    description = models.TextField(_("description"), blank=True, null=True)
    visible = models.BooleanField(_("visible"), default=True)
    order = models.IntegerField(_("order"), default=0)

    objects = models.Manager()
    current_objects = CurrentConferenceManager()

    class Meta(object):
        verbose_name = _("track")
        verbose_name_plural = _("tracks")
        ordering = ['order']

    def __unicode__(self):
        return self.name


class Location(models.Model):
    """
    A location represents a place associated with some part of the conference
    like a session room or a foyer.
    """
    conference = models.ForeignKey(Conference,
        verbose_name=_("conference"))
    name = models.CharField(_("name"), max_length=100)
    slug = models.SlugField(_("slug"))
    order = models.IntegerField(_("order"), default=0)
    used_for_sessions = models.BooleanField(_("used for sessions"),
        default=True)

    objects = models.Manager()
    current_conference = CurrentConferenceManager()

    def __unicode__(self):
        return self.name

    class Meta(object):
        verbose_name = _("location")
        verbose_name_plural = _("locations")
        ordering = ['order']


def current_conference():
    from django.conf import settings
    try:
        conf_id = settings.CONFERENCE_ID
    except AttributeError:
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured("You must set the CONFERENCE_ID setting.")
    try:
        current_conf = CONFERENCE_CACHE[conf_id]
    except KeyError:
        try:
            current_conf = Conference.objects.get(pk=conf_id)
        except Conference.DoesNotExist:
            return None
        CONFERENCE_CACHE[conf_id] = current_conf
    return current_conf
