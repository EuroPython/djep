Deployment Setup
================

Zusätzlich zu den in der Entwickler-Dokumentation erwähnten Abhängigkeiten
muss am Server auch noch LessCSS installiert sein, damit die im Projekt
vorhandenen *.less-Dateien in CSS umgewandelt werden können.

Der LessCSS-Compiler muss dann noch in django-compressor integriert werden,
was durch folgende config erfolgen kann::
    
    COMPRESS_ENABLED = True
    COMPRESS_OFFLINE = True
    COMPRESS_PRECOMPILERS = (
       ('text/less', '/srv/pyconde/local/bin/lessc -x {infile} {outfile}'),
    )

