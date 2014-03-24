.. image:: https://travis-ci.org/EuroPython/djep.png?branch=develop
   :target: https://travis-ci.org/EuroPython/djep

Installation
------------

First you have to clone this repository and all its submodules::

    git clone git@github.com:EuroPython/djep.git
    cd djep

Next create a virtualenv and install all the requirments into it. In this
example we are using virtualenvwrapper to manage the virtualenv::
    
    mkvirtualenv djep

This repository provides requirements and configurations for various
environments. Each environment (dev, staging and production) has its own
requirements.txt.

For local development, install the requirements specified in
requirements/dev.txt::

    pip install -r requirements/dev.txt

Now that this is complete, you can optionally change some settings. To get an
overview of what settings are available, take a look at the pyconde.settings
module.

We are using `django-configurations`_ to manage all settings and try to expose
all relevant settings as environment variables. By default you will probably
want to set following variables::
    
    export DJANGO_CONFIGURATION=Dev

If you want to use a different database system than PostgreSQL and a different
database than "djep", set the ``DJANGO_DATABASE_URL`` environment variable.
You can find some examples in the `dj-database-url <https://github.com/kennethreitz/dj-database-url/blob/master/test_dj_database_url.py>`_ 
test module.

Another environment variable you absolutely *have to set* is
``DJANGO_SECRET_KEY``::
    
    export DJANGO_SECRET_KEY=...

Not that this value should be constant for your local installation.

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

After this is done, you should already have a working site, but it is still
empty. To change that we have to create an admin user in order to gain access
to the admin panel::
    
    python manage.py createsuperuser

This will prompt a couple of questions you have to fill out. After this is
complete, start the development-server on port 8000 with::
    
    python manage.py runserver

As a final step you have to create a frontpage in the via
http://localhost:8000/admin/cms/page/add/.


Style integration
-----------------

Right now this project doesn't come with compiled css files but relies on
Grunt and Compass to generate them. To install them, run the following
commands. They will also install all the requirements those tools rely on::
    
    gem install --user-install compass
    npm install
    cd pyconde/skins/ep14/static/assets && ../../../../../node_modules/bower/bin/bower install

Development
-----------

During development you will probably need a dummy mail server and other
services that are usually run system-wide in production. To help you keep
all these services under control the project provides a sample Procfile
which you can use with `foreman`_ or `honcho`_::
    
    $ foreman start

or::
    
    $ honcho start

Using Vagrant
-------------

If you have `Vagrant`_ and `VirtualBox`_ installed, you can also use the
provided Vagrantfile to start a virtual machine with all the non-Python
requirements already installed::
    
    $ vagrant up

Once the virtual machine is running and you've ssh'd into it, you are already in a virtualenv
into which you can install the Python-requirements::
    
    $ cd /vagrant
    $ npm install
    $ pip install -r requirements/dev.txt

With this step also comes `honcho`_ which you can then start with ``honcho
start`` which starts the dev server on port 8000 which is exposed to port 8080
on your local host machine.

Note that you will need a filled database before this provides you a working
system. PostgreSQL is already available and running inside the virtual machine.

Deployment
----------

live: fab -c live.ini upgrade
staging: fab -c staging.ini upgrade


Base data
---------

Add a CMS page with the ID ``accounts`` and attach the ``Accounts Menu``. Make
sure to *not* display the page in the menu!


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
.. _django-configurations: http://django-configurations.readthedocs.org/en/latest/
.. _honcho: https://github.com/nickstenning/honcho
.. _vagrant: http://www.vagrantup.com/
.. _virtualbox: https://www.virtualbox.org/

