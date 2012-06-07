from cms.menu_bases import CMSAttachMenu
from menus.menu_pool import menu_pool
from menus.base import NavigationNode

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from . import utils


class ReviewsMenu(CMSAttachMenu):
    name = _("Reviews menu")

    def get_nodes(self, request):
        nodes = []
        if request.user.is_authenticated():
            if utils.can_review_proposal(request.user, None):
                nodes.append(NavigationNode("Einreichungen", reverse('reviews-available-proposals'), 'reviews-available'))
                nodes.append(NavigationNode("Meine Bewertungen", reverse('reviews-my-reviews'), 'reviews-mine'))
            nodes.append(NavigationNode("Meine Einreichungen", reverse('reviews-my-proposals'), 'reviews-my-proposals'))
        return nodes

menu_pool.register_menu(ReviewsMenu)
