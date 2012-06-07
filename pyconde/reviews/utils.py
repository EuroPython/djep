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
