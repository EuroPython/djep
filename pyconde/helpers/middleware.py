from django import http
from django.utils.http import urlquote


class CorrectDomainMiddleware(object):
    def process_request(self, request):
        host = request.get_host()
        old_url = [host, request.path]
        new_url = old_url[:]

        if host == 'de.pycon.org':
            if old_url[1].startswith('/2011/'):
                new_url[0] = '2011.de.pycon.org'
            else:
                new_url[0] = '2012.de.pycon.org'

        if new_url == old_url:
            return

        # Stolen from Django's APPEND_SLASH middleware
        if new_url[0]:
            newurl = "%s://%s%s" % (
                request.is_secure() and 'https' or 'http',
                new_url[0], urlquote(new_url[1]))
        else:
            newurl = urlquote(new_url[1])
        if request.META.get('QUERY_STRING', ''):
            newurl += '?' + request.META['QUERY_STRING']
        return http.HttpResponsePermanentRedirect(newurl)
