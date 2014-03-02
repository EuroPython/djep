Configuration
=============

This project uses `Jannis Leidel`_'s excellent `django-configurations`_ package
to provide different settings for every environment it operates in:

* development ("dev" for short)
* testing
* staging
* production

For each of these exists a configuration class within the ``pyconde.settings``
module as well as a file within the requirements folder.

To work within one of these environments first install the necessary
requirements::
    
    $ pip install requirements/dev.txt

Now you have to specify the environment with the ``DJANGO_CONFIGURATION``
environment variables for Django to know what settings to use. To execute
`syncdb`, for instance, within the "dev" environment you have to execute it
like that::
    
    $ DJANGO_CONFIGURATION=Dev python manage.py syncdb

There also exists one mandatory setting that has to be injected using an
environment variable on each machine you want to run this project:

* ``DJANGO_SECRET_KEY`` which represents Django's ``SECRET_KEY`` setting.

If you want to use PayMill for credit card payments you will also have to
inject ``DJANGO_PAYMILL_PRIVATE_KEY`` and ``DJANGO_PAYMILL_PUBLIC_KEY``. For
details what other variables you can inject through the environment please take
a look into the settings file and look for all the ``*Value`` properties as well
as the django-configurations documentation which describes what syntax to use
to inject them properly.

.. _jannis leidel: https://jezdez.com/
.. _django-configurations:
   http://django-configurations.readthedocs.org/en/latest/
