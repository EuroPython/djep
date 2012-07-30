import tablib

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


def create_simple_export(queryset):
    def _format_cospeaker(s):
        """
        Format the speaker's name for secondary speaker export and removes
        our separator characters to avoid confusion.
        """
        return unicode(s).replace("|", " ")

    queryset = queryset.select_related('duration', 'track', 'proposal',
        'speaker', 'latest_proposalversion__track', 'audience_level')
    data = tablib.Dataset(headers=['ID', 'ProposalID', 'Title',
        'SpeakerUsername', 'SpeakerName', 'CoSpeakers', 'AudienceLevel',
        'Duration', 'Track'])
    for session in queryset:
        duration = session.duration
        audience_level = session.audience_level
        track = session.track
        cospeakers = [_format_cospeaker(s) for s in session.additional_speakers.all()]
        data.append((
            session.pk,
            session.proposal.pk,
            session.title,
            session.speaker.user.username,
            unicode(session.speaker) if session.speaker else "",
            u"|".join(cospeakers),
            unicode(audience_level) if audience_level else "",
            unicode(duration) if duration else "",
            unicode(track) if track else "",
            ))
    return data
