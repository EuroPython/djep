from django import template
from .. import utils


register = template.Library()


@register.tag('qs_set')
def do_qs_set(parser, token):
    parts = token.split_contents()[1:]
    return QsSetNode([p.split("=") for p in parts])


class QsSetNode(template.Node):
    def __init__(self, params):
        self.params = params

    def render(self, context):
        params = self.convert_params(context)
        return utils.set_qs_value(context['request'].get_full_path(), params)

    def convert_params(self, context):
        return [(p[0], _resolve_variable(p[1], context)) for p in self.params]


def _resolve_variable(v, context):
    if v.startswith(('"', "'")):
        return v[1:-1]
    return template.Variable(v).resolve(context)
