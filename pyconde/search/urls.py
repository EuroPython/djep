# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from haystack.views import FacetedSearchView
from haystack.forms import FacetedSearchForm
from haystack.query import SearchQuerySet


# Now we set up the facets we want to include with every query
sqs = SearchQuerySet()
sqs = sqs.facet('django_ct')
sqs = sqs.facet('session_kind')
sqs = sqs.facet('track')
sqs = sqs.facet('tag')


urlpatterns = patterns('',
    url(r'^/?$', FacetedSearchView(searchqueryset=sqs, load_all=False,
        form_class=FacetedSearchForm)),
)
