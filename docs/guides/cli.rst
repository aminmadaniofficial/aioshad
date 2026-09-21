Command Line Interface (CLI)
=============================

``aioshad`` ships with a CLI utility for bootstrapping projects, authenticating sessions, and inspecting stored keys.

Project Initialization
----------------------

Scaffold a clean, production-ready bot boilerplate:

.. code-block:: bash

   aioshad init my_shad_bot

Interactive Terminal Login
--------------------------

Authorize a session directly from the command line without writing Python code:

.. code-block:: bash

   aioshad login --session my_account

Inspecting Session Credentials
------------------------------

View public GUID, phone number, and device info of an existing session:

.. code-block:: bash

   aioshad session-info --session my_account.session
