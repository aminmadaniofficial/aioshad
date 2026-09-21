Group Voice Chat
================

``aioshad`` supports interacting with Shad Messenger group voice chats (WebRTC voice rooms).

Creating Voice Chat
-------------------

Group administrators can initiate a group voice chat:

.. code-block:: python

   result = await client.create_voice_chat(group_guid="g0abc...")
   voice_chat_id = result.get("voice_chat_id")

Joining Voice Chat
------------------

.. code-block:: python

   await client.join_voice_chat(
       group_guid="g0abc...",
       voice_chat_id=voice_chat_id
   )

Controlling Mic and Status
--------------------------

.. code-block:: python

   # Unmute / request to speak
   await client.change_voice_chat_voice_status(
       group_guid="g0abc...",
       voice_chat_id=voice_chat_id,
       status="speaking"
   )

Leaving Voice Chat
------------------

.. code-block:: python

   await client.leave_voice_chat(
       group_guid="g0abc...",
       voice_chat_id=voice_chat_id
   )
