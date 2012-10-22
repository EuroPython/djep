from django.template import Library
from .. import slides
from django.core.cache import cache


register = Library()


@register.inclusion_tag('schedule/tags/embed_slides.html')
def embed_slides(url):
    key = "slidecache:" + url
    embed_code = cache.get(key)
    if not embed_code:
        embed_code = slides.generate_embed_code(url)
        cache.set(key, embed_code)
    return {
        'url': url,
        'embed_code': embed_code
    }
