Deployment Setup
================

Zusätzlich zu den in der Entwickler-Dokumentation erwähnten Abhängigkeiten
muss am Server auch noch LessCSS installiert sein, damit die im Projekt
vorhandenen \*.less-Dateien in CSS umgewandelt werden können.

Der LessCSS-Compiler muss dann noch in django-compressor integriert werden,
was durch folgende config erfolgen kann::
    
    COMPRESS_ENABLED = True
    COMPRESS_OFFLINE = True
    COMPRESS_PRECOMPILERS = (
       ('text/less', '/srv/pyconde/local/bin/lessc -x {infile} {outfile}'),
    )


Deployment & Systemaufbau
-------------------------

Für PyConDE haben wir in der Regel 3 Systeme:

1. Lokales Entwicklungssystem
2. Stage-System
3. Produktivsystem

Während wir für die lokale Entwicklung kein Deployment im eigentlichen Sinn
brauchen, existiert für die Stage- und Produktivumgebung Fabric-Script, das
den Deploymentprozess hier automatisiert.

Zunächst jedoch eine kurze Einführung zu den Umgebungen (2) und (3).


Stage- und Produktivumgebung
````````````````````````````

Stage und Prod. sind prinzipiell gleich aufgebaut: Innerhalb eines
Root-Verzeichnisses, das gleichzeitig auch eine Virtualenv darstellt,
existieren folgende Verzeichnisse:

* log
* htdocs (für statische Dateien)
* pycon_de_website (das ausgecheckte Projektverzeichnis)

Zusätzlich existiert in diesem Verzeichnis noch eine ``supervisord.conf``-Datei,
über die Django verwaltet wird.

Neben dem unterschiedlichen Root-Verzeichnis, verwenden Stage und Live
natürlich auch unterschiedliche Datenbanken, weshalb für jede Umgebung
eine eigene Settingsdatei angelegt werden sollte, welche Einstellungen von
``pyconde.conf.global_settings`` importiert. Ein solche Datei
(pyconde/settings.py) könnte so aussehen::
    
    from conf.global_settings import *

    DEBUG = TEMPLATE_DEBUG = THUMBNAIL_DEBUG = True

    MANAGERS = ADMINS

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'pyconde2013-staging',
            'USER': 'pyconde2012-staging',
            'PASSWORD': '123123123',
            'HOST': 'localhost',
            'PORT': '',
        }
    }

    CMS_USE_TINYMCE = False
    
    MEDIA_ROOT = os.path.join(PROJECT_ROOT, '..', '..', 'htdocs', 'site_media')
    STATIC_ROOT = os.path.join(PROJECT_ROOT, '..', '..', 'htdocs', 'static_media')
    COMPRESS_ENABLED = True
    COMPRESS_OFFLINE = True
    COMPRESS_PRECOMPILERS = (
       ('text/less', '/srv/pyconde/local/bin/lessc -x {infile} {outfile}'),
    )

    EMAIL_HOST = 'mail.gocept.net'
    INSTALLED_APPS += ('gunicorn',)
    DEFAULT_FROM_EMAIL = 'pyconde-stage@example.com'

Diese Beispielkonfiguration verwendet sowohl PostgreSQL als auch gunicorn, 
weshalb in dieser Umgebung auch psycopg2 und gunicorn verfürbar sein müssen.


Deployment mit Fabric
`````````````````````

Das Deployment erfolgt mittels Fabric. Hierfür empfiehlt es sich, für jede
der beiden Umgebungen ein eigenes Config-File anzulegen, das das
Verzeichnis, sowie den zu verwendenen Branch enthält. Ein Beispiel für
eine ``stage.ini`` wäre::
    
    root=/srv/pyconde/env_pyconde_2012-staging
    branch=develop

Zusätzlich benötigt man SSH-Zugriff auf den Server-Benutzer (in diesem Fall
u.a. "pyconde").

Hat man all das, reicht ein einfaches ``fab -c stage.ini upgrade`` um die
aktuelle Stage-Umgebung neu zu deployen.
