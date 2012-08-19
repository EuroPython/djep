from django.template import Library


register = Library()


@register.inclusion_tag('speakers/speaker_box.html')
def speaker_box(speaker):
    try:
        profile = speaker.user.get_profile()
    except:
        profile = None
    return {
        'name': unicode(speaker.user),
        'avatar': profile.avatar if profile else None,
        'user': speaker.user
    }
