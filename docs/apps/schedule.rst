Schedule-App
============

Implementierungsphasen
----------------------

1. Schedule wird in Form von statischem HTML eingespielt. Im Backend wird
   lediglich eine Datenstruktur zur inhaltlichen Pflege der finalen Sessions
   erstellt.

2. Umfasst die zeitliche Verwaltung der Sessions sowie diverse Exporte.


Datenstrukturen
---------------

Die Schedule-App bietet eine neue Datenstrukturen:

* Session

Die Session basiert auf dem Proposal-Datenmodell, erweitert dieses jedoch um
Informationen zu Ort und Zeit. Zusätzlich verweist eine Session optional auf
ein Proposal, aus dem sie hervorgegangen ist. Theoretisch kann ein Proposal
zu mehreren Sessions führen (da es aus Zeitgründen z.B. aufgesplittet werden
musste).

Die Zeitinformationen sind derzeit noch optional, da diese erste in Phase 2
der Umsetzung verwendet werden.



Umwandeln von Proposals in Sessions
-----------------------------------

Um ein Proposal in ein Session umzuwandeln, muss man unter /admin/proposals/proposal
die gewünschten Proposals auswählen und dann im Aktionen-Menü "Auswahl in
Sessions umwandeln" auswählen.

Proposals, zu denen bereits eine Session existiert, werden nicht erneut
umgewandelt.

Die hier erwähnte Funktionalität steht zusätztlich auch im Bereich der
Proposal-Metadaten zur Verfügung.
