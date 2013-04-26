from haystack.backends import elasticsearch_backend


class Backend(elasticsearch_backend.ElasticsearchSearchBackend):
    """
    This backend is optimized for german content and uses therefor the
    german analyzer exclusively for content fields.

    Note that some fields should be analyzed like tags, django_ct etc. Because
    of this we have to name the analyzer "snowball" which is used for content
    fields by haystack.
    """
    DEFAULT_SETTINGS = {
        'settings': {
            "analysis" : {
                "analyzer": {
                    "snowball": {
                        "type": "german"
                    }
                }
            }
        }
    }

class Engine(elasticsearch_backend.BaseEngine):
    backend = Backend
    query = elasticsearch_backend.ElasticsearchSearchQuery
