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

Die Schedule-App bietet zwei neue Datenstrukturen:

* Session
* SideEvent

Die Session basiert auf dem Proposal-Datenmodell, erweitert dieses jedoch um
Informationen zu Ort und Zeit. Zusätzlich verweist eine Session optional auf
ein Proposal, aus dem sie hervorgegangen ist. Theoretisch kann ein Proposal
zu mehreren Sessions führen (da es aus Zeitgründen z.B. aufgesplittet werden
musste).

Die Zeitinformationen sind derzeit noch optional, da diese erste in Phase 2
der Umsetzung verwendet werden.

Ein SideEvent ist zum Beispiel die Begrüßung, Lightning-Talks oder Pause. Wie
auch bei normalen Sessions können diese einem Ort und einer Zeitspanne
zugewiesen werden. Zusätzlich verfügen SideEvents über die Flags "Global" und
"Pause". Während "Pause" primär die Darstellung beeinflusst, sind globale Events
nicht an einen bestimmten Ort gebunden sondern gleichzeitig in allen aktiv.



Umwandeln von Proposals in Sessions
-----------------------------------

Um ein Proposal in ein Session umzuwandeln, muss man unter /admin/proposals/proposal
die gewünschten Proposals auswählen und dann im Aktionen-Menü "Auswahl in
Sessions umwandeln" auswählen.

Proposals, zu denen bereits eine Session existiert, werden nicht erneut
umgewandelt.

Die hier erwähnte Funktionalität steht zusätztlich auch im Bereich der
Proposal-Metadaten zur Verfügung.


Exports
-------

======================= ====== ==============================================================================================================
Name    Format Felder
======================= ====== ==============================================================================================================
Einfach                 CSV    ID, ProposalID, Title, SpeakerUsername, SpeakerName, CoSpeakers, AudienceLevel, Duration, Track
Guidebook_              CSV    title, date, start_time, end_time, location_name, track_name, description, type, audience, speaker, cospeakers
Sponsors_ (Guidebook)   CSV    name, website, description, level_code, level_name
Abschnitte_ (Guidebook) CSV    name, start, end, description
======================= ====== ==============================================================================================================

.. _Guidebook: /schedule/exports/guidebook/events.csv
.. _Sponsors: /schedule/exports/guidebook/sponsors.csv
.. _Abschnitte: /schedule/exports/guidebook/sections.csv



Schedule-Darstellung
--------------------

Die Schedule-App bietet Views zur Darstellung des gesamten Programms sowie
einzelner Sessions und Side-Events.

Der gesamte Schedule kann auf zwei Arten eingebunden werden:

* Über die Schedule-App, welche die URL /schedule/ bereitstellt
* Über das CMS-Plugin "Vollständiges Programm"

Beim Plugin muss bedacht werden, dass die Darstellung nur auf einer Seite
mit dem Page-Template "Full page width" Sinn macht.
