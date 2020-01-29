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

2. Install PostgreSQL and then run psql command in bash/cmd to create user that will own its created database:

      First remove users privileges and then drop him with optional flag if he exists

      ```
      REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM elisa;
      REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM elisa;
      REVOKE ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public FROM elisa;
      DROP USER IF EXISTS elisa;
      ```

      Remove database with optional flag if it exists

      ```
      DROP DATABASE IF EXISTS elisa;
      ```

      Create user with name and password and also some roles

      ```
      CREATE USER elisa WITH PASSWORD 'secret' CREATEDB CREATEROLE;
      ```

      Create database with owner elisa user that we created

      ```
      CREATE DATABASE elisa OWNER elisa;
      ```

3. Setting migrations:

      Remove all files and folders related to django migrations

      then run the following command :
      ```
      ./manage.py makemigrations <app_name>
            app names :
                  fei
                  school
                  requirements
                  timetables
      ```
    

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
     - initialize groups , tenants and insert initial data
          ```
          ./manage.py init_app <directory-of-data>
          ```
     - EXPLICITLY set main timetable creator by username
          ```
          ./manage.py set_user_role <username> <user_id> 1
          ```
          <user_id> -> ais_id from stuba
          1 -> number of role_id where 1 is a considered superuser

          check elisa/settings.py for different role options

      - create schemas in postgresql via command with login and specified schema you want to create. It's format should be as following ZS/LS_YYYY_YYYY
      
        **DISCLAIMER:** in order to run this command you must first run the server ( runsslserver )
          ```
          ./manage.py init_schemas <username> <schema>
          ```
	 **WARNING:** Due to django-tenants it seems that when you make changes on models and recreate migrations it doesn't seems to apply them correctly after running migrate_schemas command (Checking generated migration files and their application by command executing).
       You can run a shell script to clean the postgres database and remove remaining migration files if you wish so to make this process much more comfortable.
       The aforementioned script is located in the scripts folder executing it in the following manner :

          ./clean_script.sh clean_db.sql
       
      Then you can go ahead and repeat steps 3 , 4 and 6

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
      - **OPTIONAL** import data for specific schema entered. This script is being executed when `init_schemas` script is being run.
          ```
          ./manage.py import fei-data-new <schema>
          ```
      - or from import database using URLS defined in fei_importexport module (file `fei_importexport/urls.py`)). **TODO:** This script still needs some work to be updated since it then can build proper model definitions OR it will serve a look up functionality to check on new schema changes and then recreate it based on the previous ones.

10. Run the server:

      ```
      ./manage.py runsslserver
      ```

For general information about the development process of a Django application
refer to Django documentation. Also see docs for third party packages being used
such as Django REST framework.

## License

Elisa server is licensed under the AGPLv3. See LICENSE for more details.
