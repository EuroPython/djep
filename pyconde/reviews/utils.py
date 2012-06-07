from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse


def can_review_proposal(user, proposal=None):
    if user.has_perm('reviews.add_review'):
        return True
    return False


def can_participate_in_review(user, proposal):
    if can_review_proposal(user, proposal):
        return True
    if is_proposal_author(user, proposal):
        return True
    return False


def is_proposal_author(user, proposal):
    if user.speaker_profile == proposal.speaker or user.speaker_profile in proposal.additional_speakers.all():
        return True
    return False


def merge_comments_and_versions(comments, versions):
    def _comparator(a, b):
        return cmp(a.pub_date, b.pub_date)
    return sorted(list(comments) + list(versions), cmp=_comparator)


def get_people_to_notify(proposal, current_user=None):
    """
    Generates a set of all users that are somehow related to the given proposal.
    If a current_user is specified, this user will NOT be included in this set.
    """
    people_to_notify = set()
    people_to_notify.update([u.author for u in proposal.comments.select_related('author')])
    people_to_notify.update([review.user for review in proposal.reviews.all().select_related('user')])
    people_to_notify.add(proposal.speaker.user)
    people_to_notify.update([s.user for s in proposal.additional_speakers.all()])
    if current_user:
        people_to_notify.remove(current_user)
    return people_to_notify


def send_comment_notification(comment, notify_author=False):
    """
    Send a comment notification mail to all users related to the comment's
    proposal except for the author of the comment unless notify_author=True
    is passed.
    """
    proposal = comment.proposal
    current_user = comment.author
    if notify_author:
        current_user = None
    body = render_to_string('reviews/emails/comment_notification.txt', {
        'comment': comment,
        'proposal': proposal,
        'site': Site.objects.get_current(),
        'proposal_url': reverse('reviews-proposal-details', kwargs={'pk': proposal.pk}),
        })
    msg = EmailMessage(subject='[REVIEW] {0} hat {1} kommentiert'.format(comment.author, proposal.title),
        bcc=[u.email for u in get_people_to_notify(proposal, current_user)],
        body=body)
    msg.send()


def send_proposal_update_notification(version, notify_author=False):
    """
    Send a version notification mail to all users related to the version's
    proposal except for the author of the version unless notify_author=True
    is passed.
    """
    proposal = version.original
    current_user = version.creator
    if notify_author:
        current_user = None
    body = render_to_string('reviews/emails/version_notification.txt', {
        'version': version,
        'proposal': proposal,
        'site': Site.objects.get_current(),
        'proposal_url': reverse('reviews-proposal-details', kwargs={'pk': proposal.pk}),
        })
    msg = EmailMessage(subject='[REVIEW] {0} hat {1} aktualisiert'.format(version.creator, proposal.title),
        bcc=[u.email for u in get_people_to_notify(proposal, current_user)],
        body=body)
    msg.send()
