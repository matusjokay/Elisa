# Elisa server

Elisa is a prototype timetabling system for schools and universities. This is a
reference server implementation which includes a JSON RESTful web service.

## System requirements

- Python 3.6
- PostgreSQL 10 (or higher)

Tested on Ubuntu 16.04 with upstream Python 3.5.2 and PostgreSQL from repos.

## Development

We recommend using virtual environment to manage dependencies. To run locally:

1. Install dependecies:

      ```
      pip install -r requirements.txt
      ```

2. Create PostgreSQL database:

      ```
      createuser -d elisa
      createdb -O elisa elisa
      ```

3. Set up database access:

      If you are using the default PostgreSQL configuration, chances are you will
      have to create a password for the newly created user in order to be able to
      use it in Django:
    
      ```
      psql
      ALTER USER elisa WITH PASSWORD 'secret';
      ```
      
      Add the chosen password to database settings (file `elisa/settings.py`). See
      relevant
      Django [doc](https://docs.djangoproject.com/en/2.2/ref/databases/).

4. Install development ssl server:

      ```
      pip install django-sslserver
      ```
     
5. Create database tables:

      ```
      ./manage.py migrate_schemas --shared
      ```
      
      More info in django-tenants [doc](https://django-tenants.readthedocs.io/en/latest/)

6. On server where application is run, you have to run these commands:
     - initialize groups and tenants
          ```
          ./manage.py init_app
          ```
     - set main timetable creator by username
          ```
          ./manage.py set_superuser <username>
          ```

7. Install required software to work with Oracle databases depending on yor OS. More info in cx-oracle
    [doc](https://cx-oracle.readthedocs.io/en/latest/installation.html)

8. Create file `elisa-server/settings.ini` or `elisa-server/settings.env` and override these settings:
      ```
      SECRET_KEY
      DEBUG
      ALLOWED_HOSTS
      LDAP_AUTH_URL
      LDAP_AUTH_SEARCH_BASE
        
      # AIS DB settings
      DB_IMPORT_NAME
      DB_IMPORT_USER
      DB_IMPORT_PASSWORD
      DB_IMPORT_HOST
      DB_IMPORT_PORT
      ```
      
      These settings can be also set as environment variables. More info in Python Decouple
    [doc](https://github.com/henriquebastos/python-decouple)

9. Import data:
      - from csv files
          ```
          ./manage.py import fei-data <schema>
          ```
      - or from import database using URLS defined in fei_importexport module (file `fei_importexport/urls.py`)).

10. Run the server:

      ```
      ./manage.py runsslserver
      ```

For general information about the development process of a Django application
refer to Django documentation. Also see docs for third party packages being used
such as Django REST framework.

## License

Elisa server is licensed under the AGPLv3. See LICENSE for more details.
