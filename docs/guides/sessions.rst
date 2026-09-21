Session Storage
===============

``aioshad`` provides flexible and secure session management. A session stores authentication keys, user GUID, device profile, and temporary authorization tokens so that you do not need to re-enter OTP codes upon application restarts.

Session Backends
----------------

``aioshad`` includes three built-in session storage backends:

1. **FileSessionStorage** (Default)
   Saves session credentials in a JSON file with `.session` extension.
   Ideal for simple bots and local scripts.

2. **SQLiteSessionStorage**
   Stores session data inside an ACID-compliant SQLite database file.
   Supports multiple sessions concurrently in one database.

3. **MemorySessionStorage**
   Keeps session data purely in RAM for testing or short-lived serverless tasks.

File Session Example
--------------------

.. code-block:: python

   from aioshad import Client
   from aioshad.session import FileSessionStorage

   storage = FileSessionStorage("account1.session")
   client = Client(session=storage)

You can also pass a string path directly:

.. code-block:: python

   client = Client(session="account1")
   # Automatically resolves to account1.session

SQLite Session Example
----------------------

.. code-block:: python

   from aioshad import Client
   from aioshad.session import SQLiteSessionStorage

   storage = SQLiteSessionStorage("sessions.db", session_name="bot_main")
   client = Client(session=storage)

Security Best Practices
-----------------------

- Never commit `.session` or `.db` files into public git repositories.
- Add `*.session` and `*.db` to your `.gitignore`.
- On Linux servers, restrict session file permissions:

.. code-block:: bash

   chmod 600 *.session
