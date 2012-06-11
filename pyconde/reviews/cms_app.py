from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

from django.utils.translation import ugettext_lazy as _

from .menu import ReviewsMenu


class ReviewsApp(CMSApp):
    name = _("Reviews app")
    urls = ["pyconde.reviews.urls"]
    menus = [ReviewsMenu]

apphook_pool.register(ReviewsApp)
