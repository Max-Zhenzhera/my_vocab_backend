****************
My Vocab Backend
****************
| **Stack**: ``FastAPI Uvicorn Gunicorn``.

| Before: investigate ``.env.example`` and fill ``.env.[prod/dev/test]``.
| Note: for ``prod`` you have to generate local SSL cert and tweak *hosts* to local run (will describe it's later).

Run in Docker
=============
| ``Test`` [tests (pytest), linting (flake8, isort), type-checking (mypy)]:
.. code-block:: bash

    $ make test

| ``Prod`` [Nginx + Gunicorn]:
.. code-block:: bash

    $ make prod

| ``Dev`` [Uvicorn]:
.. code-block:: bash

    $ make dev

| Clean docker stuff:
.. code-block:: bash

    $ make test-down
    $ make prod-down
    $ make dev-down
    $ make clean

Run locally
=============
| Serve **postgres** DB for app.
| [I'm sure You understand that you have to put **DB URL** to that **DB** in *.env* files.]
| Put ``APP_ENV`` in **.env/environment**.

| ``Test``:
.. code-block:: bash

    $ make local-test
    # or
    $ make lint
    $ pytest

| ``Prod``:
.. code-block:: bash

    $ python app/__main__.py

| ``Dev``:
.. code-block:: bash

    $ python app/__main__.py

| ``Prod`` and ``Dev`` runners depend on ``APP_ENV`` variable.

Full Prod setup
===============
| Install `mkcert <https://github.com/FiloSottile/mkcert>`_.

.. code-block:: bash

    $ mkcert api.myvocab.io localhost 127.0.0.1 ::1

| Put this cert under *./nginx/certs*. [Use other domains? Substitute all occurrences]
| Link cert to nginx conf.d (to local run):

.. code-block:: bash

    $ cd /etc/nginx/conf.d
    $ ln -s <path-to-cert> .
    $ ln -s <path-to-cert-key> .

| Tweak */etc/hosts* file:
.. code-block:: bash

    ...
    # custom domains
    127.0.0.1       gunicorn_host
    127.0.0.1       api.myvocab.io

| You're ready to run both as locally as in Docker.
| Serve **nginx** to local run.

Afterwords
==========
``noli esse irrumatus - pone stellam.``