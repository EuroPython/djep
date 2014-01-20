class TicketNotAvailable(RuntimeError):
    def __init__(self, ticket_type):
        self.ticket_type = ticket_type
