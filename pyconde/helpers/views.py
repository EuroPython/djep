# -*- coding: utf-8 -*-
from django.conf import settings
from django.http import HttpResponseServerError
from django.template import Context, loader
from django.views.decorators.csrf import requires_csrf_token

from sekizai.data import SekizaiDictionary
from sekizai.settings import VARNAME


@requires_csrf_token
def server_error(request, template_name='500.html'):
    template = loader.get_template(template_name)
    context = Context({
        'request': request,
        'STATIC_URL': settings.STATIC_URL,
        VARNAME: SekizaiDictionary(),
    })
    return HttpResponseServerError(template.render(context))
