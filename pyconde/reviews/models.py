import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import models as auth_models

from pyconde.proposals import models as proposals_models


RATING_CHOICES = (
    ('-1', '-1'),
    ('-0', '-0'),
    ('+0', '+0'),
    ('+1', '+1')
    )


class ProposalVersion(models.Model):
    """
    This should act as snapshot of a proposal. This way authors can make
    updates to a proposal and reviewers can check if their review still
    applies.
    """
    original = models.ForeignKey(proposals_models.Proposal)
    title = models.CharField(_("title"), max_length=100)
    description = models.TextField(_("description"), max_length=400)
    abstract = models.TextField(_("abstract"))
    creator = models.ForeignKey(auth_models.User)
    pub_date = models.DateTimeField(default=datetime.datetime.now)


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
    proposal = models.ForeignKey(proposals_models.Proposal,
        related_name="reviews")
    proposal_version = models.ForeignKey(ProposalVersion)


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
    proposal = models.ForeignKey(proposals_models.Proposal,
        related_name="comments")
    proposal_version = models.ForeignKey(ProposalVersion)
