from django.views import generic as generic_views
import json
from django.http import HttpResponse
from django.contrib.auth import models as auth_models
from django.db.models import Q


class AutocompleteUser(generic_views.View):
    def get(self, request):
        term = request.GET['term']
        result = []
        for user in auth_models.User.objects.filter(
                Q(first_name=term) | Q(last_name=term)):
            result.append({
                'label': u'{0} {1}'.format(user.first_name, user.last_name),
                'value': user.speaker_profile.pk
            })
        return HttpResponse(json.dumps(result))
