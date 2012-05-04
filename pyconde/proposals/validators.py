import re

from django.core import validators as core_validators

RE_DOUBLE_WS = re.compile(r'\s\s+')


class MaxWordsValidator(core_validators.BaseValidator):
    message = "Dieses Feld darf nicht mehr als %(limit_value)s Worte enthalten"

    def compare(self, value, limit):
        normalized_value = RE_DOUBLE_WS.subn(' ', value)[0]
        num_words = len(normalized_value.split(" "))
        return num_words > limit


class MaxLengthValidator(core_validators.MaxLengthValidator):
    message = "Dieses Feld darf nicht mehr als %(limit_value)s Zeichen enthalten"
