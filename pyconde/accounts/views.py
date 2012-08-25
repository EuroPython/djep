from django.views import generic as generic_views
import json
from django.http import HttpResponse
from django.contrib.auth import models as auth_models
from django.db.models import Q
from django.shortcuts import get_object_or_404


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


class ProfileView(generic_views.TemplateView):
    """
    Displays a profile page for the given user. If the user also has a
    speaker_profile, also render the information given there.
    """

    template_name = 'userprofiles/profile_view.html'

    def get_context_data(self, uid):
        user = get_object_or_404(auth_models.User, pk=uid)
        speaker_profile = user.speaker_profile
        sessions = None
        profile = user.get_profile()
        if speaker_profile:
            sessions = list(speaker_profile.sessions.all()) + list(speaker_profile.session_participations.all())
        return {
            'userobj': user,
            'speaker_profile': speaker_profile,
            'sessions': sessions,
            'profile': profile
        }
