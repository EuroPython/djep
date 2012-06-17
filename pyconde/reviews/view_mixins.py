class PrepareViewMixin(object):
    """
    A simple view mixin that combines the preparation tasks
    normally executed by dispatch into a neat helper method.
    """
    def prepare(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        self.object = self.get_object()


class OrderMappingMixin(object):
    """
    Provides some helper methods for handling order in list-
    and similar views.
    """
    order_mapping = {}
    default_order = None
    request_order_param = 'order'

    def get_request_order(self):
        order = self.request.GET.get(self.get_request_order_param(), self.get_default_order())
        if order.lstrip('-') in self.get_order_mapping():
            return order
        return self.get_default_order()

    def get_request_order_param(self):
        return self.request_order_param

    def get_order_mapping(self):
        return self.order_mapping

    def get_default_order(self):
        return self.default_order

    def get_order(self):
        order = self.get_request_order()
        dir_ = ''
        if order.startswith('-'):
            dir_ = '-'
            order = order[1:]
        fallback = self.order_mapping[self.get_default_order().lstrip('-')]
        order = self.get_order_mapping().get(order, fallback)
        return '{0}{1}'.format(dir_, order)
