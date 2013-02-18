import urlparse
import urllib


def set_facet_value(url, facet_name, facet_value):
    """
    Sets or a replaces a facet within the given URL. The query parameter
    used for this is "selected_facets" as used by haystack internally.

    Note that this parameter will appear multiple times within the query
    string if multiple facets are selected.
    """
    scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
    if not query:
        query = urllib.urlencode([('selected_facets', '{0}:{1}'.format(
            facet_name, facet_value))])
    else:
        elems = urlparse.parse_qsl(query)
        # First let's check, if there is an existing facet selection for
        # our facet
        found_idx = None
        new_value = u'{0}:{1}'.format(facet_name, facet_value)
        new_value = new_value.encode('utf-8')
        for idx, elem in enumerate(elems):
            if elem[0] == 'selected_facets' \
                    and elem[1].split(":")[0] == facet_name:
                found_idx = idx
                break
        if found_idx is not None:
            elems[found_idx] = ('selected_facets', new_value)
        else:
            elems.append(('selected_facets', new_value))
        query = urllib.urlencode(elems)
    return urlparse.urlunparse((scheme, netloc, path, params, query, fragment))


def set_qs_value(url, qsparams):
    """
    params is an iterable of name and value pairs of querystring parameters
    that should be set within the given URL.

    If one of these parameters doesn't exist it will be appended to the
    querystring.
    """
    scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
    if query is None:
        query = urllib.urlencode(qsparams)
    else:
        elems = urlparse.parse_qsl(query)
        elem_names = set([e[0] for e in elems])
        for param in qsparams:
            _set_param(elems, param[0], param[1], elem_names)
        query = urllib.urlencode(elems)
    return urlparse.urlunparse((scheme, netloc, path, params, query, fragment))


def _set_param(elems, name, value, elem_names):
    if name not in elem_names:
        elems.append((name, value))
        return
    else:
        found_idx = None
        for idx, elem in enumerate(elems):
            if elem[0] == name:
                found_idx = idx
                break
        if found_idx is not None:
            elems[found_idx] = (name, value)
        else:
            elems.append((name, value))
