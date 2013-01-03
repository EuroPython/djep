# -*- coding: utf-8 -*-
from django.conf.urls import *
from haystack.views import SearchView, FacetedSearchView
from haystack.query import SearchQuerySet
from django.conf import settings
from .forms import MultiFacetedSearchForm


if settings.HAYSTACK_SEARCH_ENGINE == 'solr':
    sqs = SearchQuerySet()

    for facet in settings.HAYSTACK_MULTISELECT_FACETS:
        sqs = sqs.facet('{{!ex={0}}}{0}'.format(facet))

    urlpatterns = patterns('',
        url(r'^/?$', FacetedSearchView(searchqueryset=sqs, load_all=False,
            form_class=MultiFacetedSearchForm)),
    )
else:
    urlpatterns = patterns('',
        url(r'^/?$', SearchView(load_all=False)),
    )
