from django.template import Library


register = Library()


@register.inclusion_tag('speakers/speaker_box.html', takes_context=True)
def speaker_box(context, speaker):
    try:
        profile = speaker.user.get_profile()
    except:
        profile = None
    return {
        'name': unicode(speaker),
        'avatar': profile.avatar if profile else None,
        'user': speaker.user,
        'STATIC_URL': context['STATIC_URL']
    }
