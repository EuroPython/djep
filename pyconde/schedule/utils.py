from . import models

from django.core.cache import cache


def proposal_is_scheduled(proposal):
    """
    Checks if a given proposal already has a session associated with it.

    Warning: This internally caches the result for 10 seconds.
    """
    proposal_pks = cache.get('proposal_pks_with_session')
    if proposal_pks is None:
        proposal_pks = set([o['proposal__pk'] for o in models.Session.objects.values('proposal__pk')])
        cache.set('proposal_pks_with_session', proposal_pks, 10)
    return proposal.pk in proposal_pks
