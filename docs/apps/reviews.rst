Reviews-App
===========

Export der bewerteten Proposals
-------------------------------

Zur einfacheren Auswertung der Proposals, können diese zusammen mit ihrem
aktuellen Score über den Admin-Bereich exportiert werden. Die entsprechende
Aktion befindet sich unter "/admin/reviews/proposalmetadata/".

Um hier nun sämtliche Proposals zu exportiert, wählt man zuerst sämtliche
Session-Vorschläge aus (hierzu gibt es auch einen Shortcut in der linken oberen
Ecke) und wählt dann unter "Aktionen" "Als CSV exportieren" aus:

.. figure:: images/reviewed_proposals_export.png
    
    Proposals können über den Proposal-Metadata-Bereich zusammen mit dem
    aktuellen Score exportiert werden.

In diesem Export sind folgende Daten enthalten:

================ ===============================================================
Header           Beschreibung
================ ===============================================================
ID               ID des Proposals
Title            Aktueller Titel des Proposals
OriginalTitle    Ursprünglicher Titel wie er während der Proposal-Phase
                 eingetragen wurde
SpeakerUsername  Benutzername des Vortragenden
SpeakerName      Voller Name des Vortragenden wenn vorhanden, ansonsten
                 Benutzername
CoSpeakers       Voller Name der Co-Speaker mit "|" getrennt
AudienceLevel    Level
Duration         Dauer der Session
Track            Ausgewählter Track
Score            Gesammelter Score zur aktuellen Zeitpunkt
NumReviews       Anzahl der derzeit vorliegenden Reviews zu diesem Proposal
================ ===============================================================


Alternativ kann dieser Export auch über den Befehl "export_proposal_scores"
durchgeführt werden.
