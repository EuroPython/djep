import datetime
import logging

from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import models as auth_models
from django.core.urlresolvers import reverse
from django.core.cache import cache

from pyconde.proposals import models as proposal_models
from pyconde.conference import models as conference_models

from . import settings

logger = logging.getLogger(__name__)

RATING_CHOICES = (
    ('-1', '-1'),
    ('-0', '-0'),
    ('+0', '+0'),
    ('+1', '+1')
    )


class ProposalsManager(conference_models.CurrentConferenceManager):
    """
    A simple manager used for filtering proposals that are available
    for review.
    """
    pass


class ProposalMetaDataManager(models.Manager):
    """
    A simple manager used for filtering proposals that are available
    for review.
    """
    pass


class Proposal(proposal_models.Proposal):
    """
    Proxies the original proposal object in order to set different
    defaults for things like the proposal listing.
    """
    class Meta(object):
        proxy = True

    objects = models.Manager()
    current_conference = ProposalsManager()

    def can_be_updated(self):
        return self.conference.get_reviews_active()

    def can_be_reviewed(self):
        return self.conference.get_reviews_active()


class ProposalMetaData(models.Model):
    """
    This model stores some metadata for proposals with regards to
    reviews.
    """
    proposal = models.OneToOneField(Proposal, verbose_name=_("proposal"),
        related_name='review_metadata')
    latest_proposalversion = models.ForeignKey("ProposalVersion",
        verbose_name=_("latest proposal version"), null=True, blank=True)
    num_comments = models.PositiveIntegerField(
        verbose_name=_("number of comments"),
        default=0)
    num_reviews = models.PositiveIntegerField(
        verbose_name=_("number of reviews"),
        default=0)
    latest_activity_date = models.DateTimeField(
        verbose_name=_("latest activity"),
        null=True, blank=True)
    latest_comment_date = models.DateTimeField(null=True, blank=True,
        verbose_name=_("latest comment"))
    latest_review_date = models.DateTimeField(null=True, blank=True,
        verbose_name=_("latest review"))
    latest_version_date = models.DateTimeField(null=True, blank=True,
        verbose_name=_("latest version"))
    score = models.FloatField(default=0.0, null=False, blank=False,
        verbose_name=_("score"))

    objects = ProposalMetaDataManager()

    @property
    def title(self):
        return self.proposal.title

    class Meta(object):
        verbose_name = _("proposal metadata")
        verbose_name_plural = _("proposal metadata")


class ProposalVersionManager(models.Manager):
    def get_latest_for(self, proposal):
        version = self.get_query_set().filter(original=proposal)\
            .order_by('-pub_date')\
            .select_related('kind', 'duration', 'audience_level', 'track',
                'speaker')
        if not version:
            return None
        return version[0]


class ProposalVersion(proposal_models.AbstractProposal):
    """
    This should act as snapshot of a proposal. This way authors can make
    updates to a proposal and reviewers can check if their review still
    applies.
    """
    original = models.ForeignKey(proposal_models.Proposal,
        verbose_name=_("original proposal"),
        related_name='versions')
    creator = models.ForeignKey(auth_models.User,
        verbose_name=_("creator"))
    pub_date = models.DateTimeField(verbose_name=_("publication date"))

    objects = ProposalVersionManager()

    def __unicode__(self):
        return u"{0} ({1})".format(self.original.title, self.pub_date)

    class Meta(object):
        verbose_name = _("proposal version")
        verbose_name_plural = _("proposal versions")


class Review(models.Model):
    """
    The review of a proposal is the "final word" of a reviewer which
    contains a rating and a verbose justification.

    The review itself is invisible to the author until the proposal has
    been marked as closed for reviews. Neither should other reviewers be able
    to read the review before that that in order not to be influenced by it.
    """
    user = models.ForeignKey(auth_models.User, verbose_name=_("user"))
    rating = models.CharField(choices=RATING_CHOICES, max_length=2,
        verbose_name=_("rating"))
    summary = models.TextField(verbose_name=_("summary"))
    pub_date = models.DateTimeField(default=datetime.datetime.now,
        verbose_name=_("publication date"))
    proposal = models.ForeignKey(Proposal, related_name="reviews",
        verbose_name=_("proposal"))
    proposal_version = models.ForeignKey(ProposalVersion, blank=True, null=True,
        verbose_name=_("proposal version"))

    class Meta(object):
        unique_together = (('user', 'proposal'),)
        verbose_name = _("review")
        verbose_name_plural = _("reviews")


class Comment(models.Model):
    """
    The whole review process also involves that every reviewer can enter
    into a discussion with the author in order to help improve the proposal
    if necessary and clear up any possible misunderstandings.

    Once a comment is made, everyone involved in the dicussion so far should
    receive a notification include the actual content of the comment.
    """
    author = models.ForeignKey(auth_models.User, verbose_name=_("author"))
    content = models.TextField(verbose_name=_("content"))
    pub_date = models.DateTimeField(default=datetime.datetime.now,
        verbose_name=_("publication date"))
    proposal = models.ForeignKey(Proposal, verbose_name=_("proposal"),
        related_name="comments")
    proposal_version = models.ForeignKey(ProposalVersion, blank=True, null=True,
        verbose_name=_("proposal version"))
    deleted = models.BooleanField(default=False, verbose_name=_("deleted"))
    deleted_date = models.DateTimeField(null=True, blank=True,
        verbose_name=_("deleted at"))
    deleted_by = models.ForeignKey(auth_models.User, null=True, blank=True,
        verbose_name=_("deleted by"),
        related_name='deleted_comments')
    deleted_reason = models.TextField(blank=True, null=True,
        verbose_name=_("deletion reason"))

    def mark_as_deleted(self, user, reason=None):
        """
        Sets the respective flags that mark this comment as deleted
        without persisting these changes.
        """
        self.deleted = True
        self.deleted_by = user
        self.deleted_date = datetime.datetime.now()
        self.deleted_reason = reason

    def get_absolute_url(self):
        return reverse('reviews-proposal-details', kwargs={'pk': self.proposal.pk}) + '#comment-' + self.pk

    class Meta(object):
        verbose_name = _('comment')
        verbose_name_plural = _('comments')


def create_proposal_metadata(sender, instance, **kwargs):
    """
    Checks if we have a metadata object and create it if it is missing.
    """
    if isinstance(instance, proposal_models.Proposal) and not isinstance(instance, Proposal):
        prop = Proposal()
        prop.__dict__ = instance.__dict__
    else:
        prop = instance
    try:
        ProposalMetaData.objects.get(proposal=prop)
    except ProposalMetaData.DoesNotExist:
        md = ProposalMetaData(proposal=prop)
        md.save()


def _update_proposal_metadata(proposal):
    if isinstance(proposal, proposal_models.Proposal)  and not isinstance(proposal, Proposal):
        # Ugly but we have to convert this instance into our proxy model here
        # for the signal hander also to work in the admin.
        prop = Proposal()
        prop.__dict__ = proposal.__dict__
        proposal = prop
    try:
        md = proposal.review_metadata
    except ProposalMetaData.DoesNotExist:
        md = ProposalMetaData(proposal=proposal)
    md.num_comments = proposal.comments.count()
    md.num_reviews = proposal.reviews.count()

    latest_comment_date = None
    latest_review_date = None
    latest_version_date = None

    try:
        latest_version = ProposalVersion.objects.get_latest_for(proposal)
        md.latest_proposalversion = latest_version
        if latest_version:
            latest_version_date = latest_version.pub_date
    except Exception:
        logger.debug("Failed to fetch latest version of proposal", exc_info=True)
        md.latest_proposalversion = None

    score = 0.0
    try:
        latest_comment_date = proposal.comments.order_by('-pub_date')[0].pub_date
    except:
        pass
    try:
        for review in proposal.reviews.order_by('pub_date'):
            latest_review_date = review.pub_date
            score += settings.RATING_MAPPING[review.rating]
    except:
        pass
    if latest_comment_date and latest_version_date:
        if latest_comment_date > latest_version_date:
            md.latest_activity_date = latest_comment_date
        else:
            md.latest_activity_date = latest_version_date
    elif latest_comment_date:
        md.latest_activity_date = latest_comment_date
    else:
        md.latest_activity_date = latest_review_date

    md.latest_comment_date = latest_comment_date
    md.latest_review_date = latest_review_date
    md.latest_version_date = latest_version_date
    md.score = score
    md.save()


def update_proposal_metadata(sender, instance, **kwargs):
    if isinstance(instance, ProposalVersion):
        proposal = instance.original
    else:
        proposal = instance.proposal
    _update_proposal_metadata(proposal)


def clear_reviewer_cache(sender, instance, **kwargs):
    logger.debug("Clearing reviewer_pks cache")
    cache.delete('reviewer_pks')


signals.post_save.connect(create_proposal_metadata, sender=proposal_models.Proposal, dispatch_uid='reviews.proposal_metadata_creation')
signals.post_save.connect(update_proposal_metadata, sender=Comment, dispatch_uid='reviews.update_proposal_comments_count')
signals.post_save.connect(update_proposal_metadata, sender=Review, dispatch_uid='reviews.update_proposal_reviews_count')
signals.post_save.connect(update_proposal_metadata, sender=ProposalVersion, dispatch_uid='reviews.update_proposal_version_count')
signals.post_delete.connect(update_proposal_metadata, sender=Comment, dispatch_uid='reviews.update_proposal_comments_count_del')
signals.post_delete.connect(update_proposal_metadata, sender=Review, dispatch_uid='reviews.update_proposal_reviews_count_del')
signals.post_delete.connect(update_proposal_metadata, sender=ProposalVersion, dispatch_uid='reviews.update_proposal_version_count_del')
signals.post_save.connect(clear_reviewer_cache, sender=auth_models.User, dispatch_uid='reviews.clear_reviewer_cache')
signals.post_delete.connect(clear_reviewer_cache, sender=auth_models.User, dispatch_uid='reviews.clear_reviewer_cache_del')
signals.post_save.connect(clear_reviewer_cache, sender=auth_models.Permission, dispatch_uid='reviews.clear_reviewer_cache_perm')
signals.post_delete.connect(clear_reviewer_cache, sender=auth_models.Permission, dispatch_uid='reviews.clear_reviewer_cache_perm_del')
signals.post_save.connect(clear_reviewer_cache, sender=auth_models.Group, dispatch_uid='reviews.clear_reviewer_group')
signals.post_delete.connect(clear_reviewer_cache, sender=auth_models.Group, dispatch_uid='reviews.clear_reviewer_group_del')
