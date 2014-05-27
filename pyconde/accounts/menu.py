# -*- encoding: UTF-8 -*-
from cms.menu_bases import CMSAttachMenu
from menus.menu_pool import menu_pool
from menus.base import NavigationNode

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse


class AccountsMenu(CMSAttachMenu):
    """
    Menu for the accounts app which provides access to the profile rendering
    and change form as well as the change password form.
    """
    name = _("Accounts menu")

    def get_nodes(self, request):
        nodes = []
        if request.user.is_authenticated():
            # nodes.append(NavigationNode(_("Your profile"), reverse('account_profile', kwargs={'uid': request.user.pk}), 'account-profile'))
            nodes.append(NavigationNode(_("Change your profile"), reverse('userprofiles_profile_change'), 'account-change-profile'))
            nodes.append(NavigationNode(_("Change your password"), reverse('auth_password_change'), 'account-change-password'))
            nodes.append(NavigationNode(_("Purchases"), reverse('attendees_user_purchases'), 'account-purchases'))
            nodes.append(NavigationNode(_("Tickets"), reverse('attendees_user_tickets'), 'account-tickets'))
            nodes.append(NavigationNode(_("Session attendances"), reverse('schedule-attendances'), 'schedule-attendances'))
            nodes.append(NavigationNode(_("Logout"), reverse('auth_logout'), 'account-logout'))
        return nodes

menu_pool.register_menu(AccountsMenu)
