import datetime

from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import models as auth_models

from pyconde.proposals import models as proposal_models
from pyconde.conference import models as conference_models


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
    def get_query_set(self):
        if not conference_models.current_conference().get_reviews_active():
            return super(ProposalsManager, self).get_query_set().none()
        return super(ProposalsManager, self).get_query_set().all()


class ProposalMetaDataManager(models.Manager):
    """
    A simple manager used for filtering proposals that are available
    for review.
    """
    def get_query_set(self):
        if not conference_models.current_conference().get_reviews_active():
            return super(ProposalMetaDataManager, self).get_query_set().none()
        return super(ProposalMetaDataManager, self).get_query_set().all()


class Proposal(proposal_models.Proposal):
    """
    Proxies the original proposal object in order to set different
    defaults for things like the proposal listing.
    """
    class Meta(object):
        proxy = True

    objects = ProposalsManager()

    def can_be_updated(self):
        return self.conference.get_reviews_active()

    def can_be_reviewed(self):
        return self.conference.get_reviews_active()


class ProposalMetaData(models.Model):
    """
    This model stores some metadata for proposals with regards to
    reviews.
    """
    proposal = models.OneToOneField(Proposal, related_name='review_metadata')
    num_comments = models.PositiveIntegerField(default=0)
    num_reviews = models.PositiveIntegerField(default=0)
    latest_activity_date = models.DateTimeField(null=True, blank=True)
    latest_comment_date = models.DateTimeField(null=True, blank=True)
    latest_review_date = models.DateTimeField(null=True, blank=True)

    objects = ProposalMetaDataManager()

    @property
    def title(self):
        return self.proposal.title


class ProposalVersionManager(models.Manager):
    def get_latest_for(self, proposal):
        version = self.get_query_set().filter(original=proposal).order_by('-pub_date')
        if not version:
            return None
        return version[0]


class ProposalVersion(proposal_models.AbstractProposal):
    """
    This should act as snapshot of a proposal. This way authors can make
    updates to a proposal and reviewers can check if their review still
    applies.
    """
    original = models.ForeignKey(proposal_models.Proposal, related_name='versions')
    creator = models.ForeignKey(auth_models.User)
    pub_date = models.DateTimeField()

    objects = ProposalVersionManager()

    def __unicode__(self):
        return "{0} ({1})".format(self.original.title, self.pub_date)

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
    user = models.ForeignKey(auth_models.User)
    rating = models.CharField(choices=RATING_CHOICES, max_length=2)
    summary = models.TextField()
    pub_date = models.DateTimeField(default=datetime.datetime.now)
    proposal = models.ForeignKey(Proposal, related_name="reviews")
    proposal_version = models.ForeignKey(ProposalVersion, blank=True, null=True)

    class Meta(object):
        unique_together = (('user', 'proposal'),)


class Comment(models.Model):
    """
    The whole review process also involves that every reviewer can enter
    into a discussion with the author in order to help improve the proposal
    if necessary and clear up any possible misunderstandings.

    Once a comment is made, everyone involved in the dicussion so far should
    receive a notification include the actual content of the comment.
    """
    author = models.ForeignKey(auth_models.User)
    content = models.TextField()
    pub_date = models.DateTimeField(default=datetime.datetime.now)
    proposal = models.ForeignKey(Proposal,
        related_name="comments")
    proposal_version = models.ForeignKey(ProposalVersion, blank=True, null=True)
    deleted = models.BooleanField(default=False)
    deleted_date = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(auth_models.User, null=True, related_name='deleted_comments')
    deleted_reason = models.TextField(blank=True, null=True)

    def mark_as_deleted(self, user, reason=None):
        """
        Sets the respective flags that mark this comment as deleted
        without persisting these changes.
        """
        self.deleted = True
        self.deleted_by = user
        self.deleted_date = datetime.datetime.now()
        self.deleted_reason = reason


def create_proposal_metadata(sender, instance, **kwargs):
    """
    Checks if we have a metadata object and create it if it is missing.
    """
    try:
        ProposalMetaData.objects.get(proposal=instance)
    except ProposalMetaData.DoesNotExist:
        md = ProposalMetaData(proposal=instance)
        md.save()


def _update_proposal_metadata(proposal):
    try:
        md = proposal.review_metadata
    except ProposalMetaData.DoesNotExist:
        md = ProposalMetaData(proposal=proposal)
    md.num_comments = proposal.comments.count()
    md.num_reviews = proposal.reviews.count()

    latest_comment_date = None
    latest_review_date = None
    try:
        latest_comment_date = proposal.comments.order_by('-pub_date')[0].pub_date
    except:
        pass
    try:
        latest_review_date = proposal.reviews.order_by('-pub_date')[0].pub_date
    except:
        pass
    if latest_comment_date and latest_review_date:
        if latest_comment_date > latest_review_date:
            md.latest_activity_date = latest_comment_date
        else:
            md.latest_activity_date = latest_review_date
    elif latest_comment_date:
        md.latest_activity_date = latest_comment_date
    else:
        md.latest_activity_date = latest_review_date
    md.latest_comment_date = latest_comment_date
    md.latest_review_date = latest_review_date
    md.save()


def update_proposal_metadata(sender, instance, **kwargs):
    proposal = instance.proposal
    _update_proposal_metadata(proposal)

signals.post_save.connect(create_proposal_metadata, sender=proposal_models.Proposal, dispatch_uid='reviews.proposal_metadata_creation')
signals.post_save.connect(update_proposal_metadata, sender=Comment, dispatch_uid='reviews.update_proposal_comments_count')
signals.post_save.connect(update_proposal_metadata, sender=Review, dispatch_uid='reviews.update_proposal_reviews_count')
