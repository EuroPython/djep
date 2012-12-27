from haystack.forms import FacetedSearchForm
from django.conf import settings


class MultiFacetedSearchForm(FacetedSearchForm):
    def search(self):
        sqs = super(FacetedSearchForm, self).search()
        multiselect_facets = set(getattr(settings, 'HAYSTACK_MULTISELECT_FACETS', []))
        # We need to process each facet to ensure that the field name and the
        # value are quoted correctly and separately:
        for facet in self.selected_facets:
            if ":" not in facet:
                continue

            field, value = facet.split(":", 1)

            if field in multiselect_facets:
                field = "{{!tag={0}}}{0}".format(field)

            if value:
                sqs = sqs.narrow(u'%s:"%s"' % (field, sqs.query.clean(value)))

        return sqs
