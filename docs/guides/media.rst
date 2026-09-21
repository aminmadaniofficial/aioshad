Media Upload and Download
==========================

``aioshad`` handles encrypted file chunking, parallel streaming uploads, and automated thumbnail extraction.

Sending Photos
--------------

.. code-block:: python

   await client.send_photo(
       chat_id="g0abc...",
       photo="path/to/image.jpg",
       caption="Check out this photo!"
   )

Sending Documents & Files
-------------------------

Any file format can be transmitted as a file/document:

.. code-block:: python

   await client.send_file(
       chat_id="g0abc...",
       file="report.pdf",
       caption="Quarterly Report PDF"
   )

Sending Voice Notes
-------------------

.. code-block:: python

   await client.send_voice(
       chat_id="u0abc...",
       voice="voice_note.ogg",
       duration=12
   )

Downloading Files
-----------------

Download media from received messages directly:

.. code-block:: python

   @client.on_message()
   async def handle_incoming_file(msg: Message):
       if msg.file:
           file_path = await client.download_file(
               file=msg.file,
               destination=f"./downloads/{msg.file.file_name}"
           )
           await msg.reply(f"File downloaded to {file_path}")
