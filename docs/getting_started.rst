Getting Started
===============

Install
-------

.. code-block:: bash

   pip install modelvault

For development:

.. code-block:: bash

   pip install -e ".[dev]"

Quick example
-------------

Define a Pydantic model, decorate it with a persistence contract, and use a typed
collection backed by SQLite:

.. code-block:: python

   from pydantic import BaseModel, EmailStr
   from modelvault import Vault, model

   @model(key="id", storage="table")
   class User(BaseModel):
       id: int
       email: EmailStr
       active: bool = True

   vault = Vault.sqlite("app.db")
   users = vault.collection(User)

   users.insert(User(id=1, email="alice@example.com"))
   user = users.get(1)

   print(user.email)

Core concepts
-------------

**Persistence contract**
   Declared via ``@model(key=..., storage=..., indexes=...)``. Describes how a
   Pydantic model is stored.

**Vault**
   Root coordinator for a single database. Creates collections and runs health checks.

**Collection**
   Typed repository for one model: insert, get, upsert, delete, find, and more.
   Returns validated Pydantic instances on every read.

v0.17 scope
-----------

Current release (0.17.0) includes:

- SQLite via SQLAlchemy Core
- Table storage only
- Read/write validation
- Registry metadata and contract fingerprints
- Basic drift detection

See :doc:`roadmap` for upcoming versions.
