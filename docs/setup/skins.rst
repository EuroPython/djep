Skins
=====

Dieser Abschnitt beschreibt die Erstellung eines neuen Skins für die
Konferenzsoftware. Im Wesentlichen wird ein neues Skin erstellt, indem
Basis-Templates, Styles und Grafikelement hinzugefügt und eingerichtet
werden.


Skins sind als Django-Apps realisiert und werden zur besseren
Übersichtlichkeit im Skin-Verzeichnis :file:`pyconde/skins/` abgelegt.

Um ein neues Skin zu erstellen wird eine neue App im Skin-Verzeichnis
mit der folgenden Dateistruktur angelegt::

  +- skins/
    +- myskin/
    | |- __init__.py
    | |- views.py
    | |- models.py
    | +- templates/
    | |  |- base.html
    | |  |- ...
    | +- static/
    | |  +- css/
    | |  |  |- style.less
    | |  |  |- ...
    | |  +- images/
    | |  |  |- ...
    | |  +- js/
    | |  |  |- ...

Die Dateien :file:`__init__.py`, :file:`views.py` und
:file:`models.py` können dabei leer
bleiben. :file:`templates/base.html` sollte von
:file:`site_structure.html` abgeleitet
sein. :file:`static/css/style.less` wird beim Deployment zur
Generierung der CSS-Dateien verwenden.

Der Default-Skin stellt eine Reihe an Templates bereit, die von
anderen Applikationen, wie zum Beispiel dem CMS, benötigt
werden. Daher sollte neben ``myskin`` auch das Default-Skin
eingebunden werden und zwar derart, dass das Default-Skin nach dem
eigenen Skin von Django betrachtet wird:

.. code-block:: python

  INSTALLED_APPS = (
      ...
      # Skins
      'pyconde.skins.myskin',
      'pyconde.skins.default',
      ...
  )

Die Datei :file:`pyconde/skins/default/templates/base.html` bietet
eine gute Vorlage für ein Basis-Template im eigenen Skin, indem es
die wichtigsten Blöcke und Template-Tags, die zur vollständigen
Darstellung benötigt werden aufzeigt.
