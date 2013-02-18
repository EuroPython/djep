import re

from django.test.client import RequestFactory
from django.template import RequestContext

from haystack import indexes

from cms import models as cmsmodels


rf = RequestFactory()

HTML_TAG_RE = re.compile(r'<[^>]+>')


def cleanup_content(s):
    """
    Removes HTML tags from data and replaces them with spaces.
    """
    return HTML_TAG_RE.subn('', s)[0]


class PageIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Since for now we only offer this site in one language, we can get around
    by not doing any language model hacks.
    """
    text = indexes.CharField(document=True)
    title = indexes.CharField()
    url = indexes.CharField()

    def get_model(self):
        return cmsmodels.Page

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(published=True)

    def prepare(self, obj):
        self.prepared_data = super(PageIndex, self).prepare(obj)
        request = rf.get('/')
        request.session = {}
        text = u""
        # Let's extract the title
        context = RequestContext(request)
        for title in obj.title_set.all():
            self.prepared_data['title'] = title.title
        for placeholder in obj.placeholders.all():
            text += placeholder.render(context, None)
        self.prepared_data['text'] = cleanup_content(
            self.prepared_data['title'] + text)
        self.prepared_data['url'] = obj.get_absolute_url()
        return self.prepared_data
