.. image:: https://secure.travis-ci.org/zerok/pyconde-website-mirror.png

Installation
------------

First you have to clone this repository and all its submodules::

    git clone git@bitbucket.org:PySV/pycon_de_website.git
    cd pycon_de_website
    git submodule init
    git submodule update

Next create a virtualenv and install all the requirments into it. In this
example we are using virtualenvwrapper to manage the virtualenv::
    
    mkvirtualenv pyconde_website
    workon pyconde_website
    pip install -r requirements.txt

Now that this is complete, prepare the settings::

    cd pyconde
    cp settings.py.dist settings.py
    cd ..

Everything should be in place now to initialize the database. If you want to use
SQLite be warned that there are some issues with the migration steps done
for some of django-cms' plugins. Therefor you will most likely have to run
this::
    
    python manage.py syncdb --noinput --all
    python manage.py migrate --fake

If you want to use PostgreSQL (which is also used in production for this site),
alter the `DATABASES` section of your pyconde/settings.py accordingly and then
run following command::
    
    python manage.py syncdb --noinput --migrate

For PyCONDE we have prepared a bunch of fixtures that provide some basic
conference data::
    
    python manage.py loaddata fixtures/conference-setup.json
    python manage.py loaddata tickets2012
    python manage.py loaddata pyconde2012-tracks.json

After this is done, you should already have a working site, but it is still
empty. To change that we have to create an admin user in order to gain access
to the admin panel::
    
    python manage.py createsuperuser

This will prompt a couple of questions you have to fill out. After this is
complete, start the development-server on port 8000 with::
    
    python manage.py runserver 8000

As a final step you have to create a frontpage in the via
http://localhost:8000/admin/cms/page/add/.


Development
-----------

During development you will probably need a dummy mail server and other
services that are usually run system-wide in production. To help you keep
all these services under control the project provides a sample Procfile
which you can use with `foreman`_::
    
    foreman start


Deployment
----------

live: fab -c live.ini upgrade
staging: fab -c staging.ini upgrade


Symposion
---------

Parts of this project are based on work by the Symposion/Pinax team. Apps
originating in Symposion are:

* conference
* sponsorship


Other 3rd-party components
--------------------------

This repository also contains various icons created by `Paul Robert Lloyd`_.
Every site using this component must either indicate this in the footer or
in the imprint.

.. _Paul Robert Lloyd: http://www.paulrobertlloyd.com/2009/06/social_media_icons/
.. _foreman: https://github.com/ddollar/foreman
