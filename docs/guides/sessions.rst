Session Storage
===============

A session preserves authentication credentials so your application can restart and reconnect immediately without re-requesting OTP verification codes.

Stored Data
-----------

A session safely stores:

- Decrypted AES session key and initialization vectors.
- Asymmetric RSA-1024 private key.
- Authenticated user GUID and registered phone number.
- Client device fingerprint (app version, OS version, device name).

Storage Engines
---------------

FileSessionStorage
~~~~~~~~~~~~~~~~~~

The default engine. Writes credentials into a JSON file with `.session` extension:

.. code-block:: python

   from aioshad import Client
   from aioshad.session import FileSessionStorage

   # Explicit storage object
   storage = FileSessionStorage("account1.session")
   client = Client(session=storage)

   # Or convenient string shorthand
   client = Client(session="account1")

SQLiteSessionStorage
~~~~~~~~~~~~~~~~~~~~

Ideal for multi-tenant applications or hosting multiple sessions in a single database file:

.. code-block:: python

   from aioshad import Client
   from aioshad.session import SQLiteSessionStorage

   storage = SQLiteSessionStorage("sessions.db", session_name="bot_primary")
   client = Client(session=storage)

Benefits of SQLite:

- ACID transactional safety.
- Concurrently accessible by multiple worker processes.
- Single-file backups for entire bot fleets.

MemorySessionStorage
~~~~~~~~~~~~~~~~~~~~

Stores credentials purely in memory. All state is lost upon process exit. Useful for unit tests or ephemeral containerized tasks:

.. code-block:: python

   from aioshad import Client
   from aioshad.session import MemorySessionStorage

   storage = MemorySessionStorage()
   client = Client(session=storage)

Security Recommendations
------------------------

- Always exclude session files from version control by adding ``*.session`` and ``*.db`` to your ``.gitignore``.
- Restrict file access permissions on production servers:

.. code-block:: bash

   chmod 600 *.session
   chmod 600 *.db
