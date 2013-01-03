#####
Suche
#####

Für die Suche kommt `django-haystack`_ zum Einsatz, das eine einfache Abstraktion
zu Systemen wie Solr_ und Whoosh_ bietet. Um die Suche auch tatsächlich verwenden
zu können, muss dabei noch zusätzlich entweder Whoosh oder Solr eingerichtet
werden. Für die lokale Entwicklung sollte hierbei in der Regel ersteres genügen,
jedoch mit der Einschränkung, dass Facettensuche nicht untertützt wird.

Aus diesem Grund wird Solr empfohlen. Beispiel-Settings für beide Systeme
finden sich in der ``global_settings.py``.

Sobald man entweder Solr oder Whoosh konfiguriert hat (Details siehe weiter
unten), muss man mit ``python manage.py rebuild_index`` Daten in den Suchindex
laden.

Setup
#####

Suchen mit Whoosh
=================

Für Whoosh muss nichts weiter konfiguriert werden, da die Entsprechenden
Einstellungen bereits in der global_settings.py als Fallback eingetragen sind::
    
    HAYSTACK_SEARCH_ENGINE = 'whoosh'
    HAYSTACK_WHOOSH_PATH = os.path.join(PROJECT_ROOT, 'whoosh_index')


Suchen mit Solr
===============

Für Solr müssen ein paar Extra-Schritte durchgeführt werden:

1. Zunächst muss ``pysolr`` installiert werden (``pip install pysolr``).
2. Dann muss haystack von Whoosh auf Solr umgestellt werden::
    
    HAYSTACK_SEARCH_ENGINE = 'solr'
    HAYSTACK_SOLR_URL = 'http://localhost:8983/solr/main'

3. Da Solr ein eigenständiger Dienst ist, muss dieser seperat installiert
   werden. Details dazu finden sich zum Beispiel im `Solr 4.0 Tutorial <http://lucene.apache.org/solr/4_0_0/tutorial.html>`_.

   Für die Einrichtung unter OSX empfiehlt sich Homebrew. Zusätzlich existiert
   im ``solr.dist``-Verzeichnis eine Beispielkonfiguration, die dann einfach
   mittels ``solr /absoluter/pfad/zu/solr.dist`` gestartet werden kann.

Indexers
########

Derzeit werden folgende Inhalte indiziert:

* Speakers
* CMS-Seiten (nur einsprachig)
* Sessions

Details zu den jeweils indizierten Daten finden sich in der ``search_indexes.py``
der entsprechenden Applikation.


Daten-Aktualisierung
####################

Die Index-Aktualisierung muss derzeit über Cronjob durchgeführt werden. Hierbei
würde sich ein Job anbieten, der alle 30min. den ``update_index``-Befehl
ausführt, wodurch sämtliche Daten erneut indiziert werden.

Da dieser Vorgang sehr schnell ist, existiert derzeit noch kein Post-Save-Handler,
der einzelne Dokumente im Index nach deren Speicherung aktualisiert::

    > time python manage.py update_index
    Indexing 19 pages.
    Indexing 56 speakers.
    Indexing 74 sessions.
    python manage.py update_index  1.94s user 0.18s system 81% cpu 2.585 total



.. _django-haystack: http://haystacksearch.org/
.. _whoosh: https://bitbucket.org/mchaput/whoosh/wiki/Home
.. _solr: http://lucene.apache.org/solr/