Deployment Setup
================

Deployment & System structure
-----------------------------

We currently have 3 systems:

1. Local development environment
2. Staging system
3. Production system

While for the local system you don't need any kind of deployment, we have a
Fabric script for the other two.


Staging and production environments
```````````````````````````````````

Staging and production have the same structure on the server with each having
their own virtualenv and supervisord instance to manage all the necessary
processes.

Additionally, we use envdir (with the settings stored in
``/path/to/virtualenv/env``) to provide those settings that are not already
stored in ``pyconde.settings`` for the respective environment.

Note-worthy folders:

* ``var/logs`` contains all the log files
* ``htdocs`` holds the static media files
* ``djep`` is the project's source
* ``redis`` contains Redis' configuration file and all generated snapshots


Deployment with Fabric
``````````````````````

For the deployment onto staging and production we use a Fabric script in
combination with a .ini file for each environment.

Besides Fabric you also need SSH access to the target server and the service
user. Once you have all that, just execute for instance::
    
    $ fab -c staging.ini upgrade

To deploy the current ``develop`` branch to the staging environment. Which
branch is used is configurable in the .ini file.
