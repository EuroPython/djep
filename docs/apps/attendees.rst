**********
Ticket-App
**********

Die ``attendees``-App integriert ein einfaches Ticket-Verkaufsystem in die
Website. Man kann über die Klasse ``TicketType`` neue Ticket-Typen anlegen
und ihnen einen Preis geben. Zudem kann konfiguriert werden, dass ein
Ticket eines bestimmten Typs nur dann gekauft werden kann, wenn man zudem
einen Gutschein (``Voucher``) eines bestimmten Typs zur Verfügung hat.


Gutscheine
==========

Wie eingangs erwähnt, ermöglichen Gutscheine die Einschränkung bestimmter
Tickettypen für bestimmte Kunden. Ein konkreter Use-Case wäre hier ein
Studententicket:

.. image:: images/attendees-voucher-ticket.png

Hier wurde der Tickettyp "Studententicket" so konfiguriert, dass beim Kauf
ein Gutschein vom Typ "Studentengutschein" angegeben werden muss.

Der Gutscheintyp selbst, ist nur ein einfaches Model um mehrere Gutscheine
zu bündeln. Die Gutscheine selbst, müssen manuell im Admin-Bereich angelegt
werden und können dann explizit ausgegeben werden; zum Beispiel nachdem
ein Student die Ablichtung eines Studentenausweises bereitgestellt hat.

.. warning::
    
    Wenn ein Tickettyp einen Gutschein benötigt, kann lediglich ein Ticket 
    dieses Typs pro Einkauf erstanden werden.
