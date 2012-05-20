class ListProposalsView(object):
    """
    Lists all proposals the reviewer should be able to review, sorted by
    "priority".

    This listing should include some filter functionality to filter proposals
    by tag, track or kind.

    Access: review-team
    """
    pass


class SubmitReviewView(object):
    """
    Only reviewers should be able to submit reviews as long as the proposal
    accepts one. The review-period should perhaps coincide with closing
    the proposal for discussion.

    Access: review-team
    """
    pass


class SubmitCommentView(object):
    """
    Everyone on the review-team as well as the original author should be
    able to comment on a proposal.

    Access: author and review-team
    """
    pass


class ProposalDetailsView(object):
    """
    An extended version of the details view of the proposals app that
    also includes the discussion as well as the review of the current user.

    Access: author and review-team
    """
    pass


class UpdateProposalView(object):
    """
    This should create a new version of the proposal and notify all
    contributors to the discussion so far.

    Access: author
    """


class ReviewOverviewView(object):
    """
    This view should provide the organisers with an overview of the review
    progress and should indicate how many proposals have been reviewed so far
    and their current scores.

    Access: staff
    """
    pass


class OpenProposalForReviewsView(object):
    """
    The moment a proposal is opened for reviews, a ProposalVersion is created
    in order to act as a snapshot on which the reviewers can rely on.

    Access: staff
    """
    pass
