# Elisa server

Elisa is a prototype timetabling system for schools and universities. This is a
reference server implementation which includes a JSON RESTful web service.

## System requirements

- Python 3.5
- PostgreSQL 9.5 (or higher)

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
  Django [doc](https://docs.djangoproject.com/en/1.11/ref/settings/#databases).

4. Create database tables:

  ```
  ./manage.py migrate
  ```

5. Create superuser:

  ```
  ./manage.py createsuperuser
  ```

6. Import data:

  ```
  ./manage.py import fei-data
  ```

7. Run the server:

  ```
  ./manage.py runserver
  ```

For general information about the development process of a Django application
refer to Django documentation. Also see docs for third party packages being used
such as Django REST framework.

## License

Elisa server is licensed under the AGPLv3. See LICENSE for more details.
