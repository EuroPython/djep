from haystack.indexes import SearchIndex, CharField
from django.db import connection
import haystack

from pyconde.accounts.models import Profile

from . import models


class SpeakerIndex(SearchIndex):
    """
    We index all actual speakers.
    """

    title = CharField()
    text = CharField(document=True)
    url = CharField()

    def prepare(self, obj):
        data = super(SpeakerIndex, self).prepare(obj)
        
        short_info = ""
        try:
            profile = Profile.objects.get(user=obj.user)
            short_info = profile.short_info
        except:
            pass

        data['title'] = unicode(obj)
        data['text'] = data['title'] + short_info
        data['url'] = obj.get_absolute_url()
        return data

    def index_queryset(self):
        c = connection.cursor()
        c.execute('''
            SELECT distinct(s.*)
            FROM
                schedule_session as session,
                speakers_speaker as s
            WHERE
                session.speaker_id = s.id

            UNION

            SELECT distinct(s.*)
            FROM 
                schedule_session_additional_speakers as session,
                speakers_speaker as s
            WHERE
                session.speaker_id = s.id
            ''')
        ids = [r[0] for r in c.fetchall()]
        return models.Speaker.objects.filter(id__in=ids).select_related('user')


haystack.site.register(models.Speaker, SpeakerIndex)
