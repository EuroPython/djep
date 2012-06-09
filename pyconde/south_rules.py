"""
South introspection rule for TimeZoneField

Source: http://djangosnippets.org/snippets/2395/
"""
from timezones.fields import TimeZoneField
from timezones.zones import PRETTY_TIMEZONE_CHOICES
from south.modelsinspector import add_introspection_rules, add_ignored_fields
from django.conf import settings


add_introspection_rules(rules=[
        ((TimeZoneField,),
        [],
        {
            "default": ["default", {"default": settings.TIME_ZONE}],
            "choices": ["choices", {"default": PRETTY_TIMEZONE_CHOICES}],
            "max_length": ["max_length", {"default":getattr(settings,
                "MAX_TIMEZONE_LENGTH", 100)}],
        }
        )
    ],
    patterns=['timezones\.fields', ])

add_ignored_fields(["^pyconde\.tagging"])
