from haystack.indexes import SearchIndex, CharField, MultiValueField, Indexable
from . import models


class SessionIndex(SearchIndex, Indexable):
    title = CharField(model_attr='title')
    text = CharField(document=True)
    url = CharField()
    session_kind = CharField(faceted=True)
    tags = MultiValueField(faceted=True)
    track = CharField(faceted=True)
    speaker = CharField()

    def get_model(self):
        return models.Session

    def prepare(self, obj):
        self.prepared_data = super(SessionIndex, self).prepare(obj)
        self.prepared_data['url'] = obj.get_absolute_url()
        self.prepared_data['session_kind'] = obj.kind.name
        self.prepared_data['speaker'] = unicode(obj.speaker)
        self.prepared_data['tags'] = [t.name for t in obj.tags.all()]
        self.prepared_data['track'] = obj.track.name if obj.track else None
        self.prepared_data['text'] = u"{title}\n\n{desc}\n\n{abstract}\n\n{tags}\n\n{track}\n\n{speaker}".format(
            title=obj.title,
            desc=obj.description,
            abstract=obj.abstract,
            tags=u', '.join(self.prepared_data['tags']),
            track=self.prepared_data['track'],
            speaker=self.prepared_data['speaker'])

        return self.prepared_data
