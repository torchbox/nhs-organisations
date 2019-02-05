=================
NHS Organisations
=================

django-nhs-organisations is a tiny app to help you store, use and update NHS Organisation data in your Django project.  

The current version is tested for compatiblily with the following: 

- Django versions 1.11 to 2.0
- Python version 3.6


Installation
============

1.  Install the package using pip:

    .. code-block:: console

        pip install git+https://bitbucket.org/rkhleics/nhs-organisations.git

2.  Add ``nhsorganisations`` to ``INSTALLED_APPS`` in your project settings:

    .. code-block:: python

        INSTALLED_APPS = [
            ...
            'nhsorganisations',
        ] 

3.  Run migrations:
    
    .. code-block:: console

        python manage.py migrate nhsorganisations


4. Populate data by pulling from the NHSI website:

    .. code-block:: console

        python manage.py pull_organisations_from_nhsi_site


Keeping your local data up-to-date
==================================

Currently, the NHS Improvement Corporate Website is the closest thing we have to a 'source of truth', and the only place we know of that serves the data in a way that can be easily consumed by other apps (as JSON, at the URL: https://improvement.nhs.uk/organisations.json)

So, to update your local data to reflect the source of truth, run the following command:

.. code-block:: console

    python manage.py pull_organisations_from_nhsi_site


Could this break things in my project?
--------------------------------------

Organisations are only ever 'closed', and so should never be removed from the data source once they have been created. Unless you're doing something really bizarre in your app, you shouldn't ever have to worry about unexpected data loss or knock-on effects of running this command; It will always be **atomic** and **non-destructive**.


How regularly should I update?
------------------------------

For production environments, it's recommended you set up a recurring task to call the above command once every 24 hours (some time between 1am and 4am, ideally).
