from django.template import Library

register = Library()


@register.filter
def is_editable_ticket(ticket, user):
    return ticket.can_be_edited_by(user)
