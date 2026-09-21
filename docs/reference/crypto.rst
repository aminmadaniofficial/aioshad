Cryptography Reference
======================

Details on the reverse-engineered AES-256 and RSA-1024 encryption layer used to communicate securely with Shad edge gateways.

Payload Encryption & Decryption
-------------------------------

.. autofunction:: aioshad.crypto.encrypt_payload

.. autofunction:: aioshad.crypto.decrypt_payload

AES Primitives
--------------

.. autofunction:: aioshad.crypto.aes_encrypt

.. autofunction:: aioshad.crypto.aes_decrypt

RSA Key Exchange
----------------

.. autofunction:: aioshad.crypto.create_rsa_keys

.. autofunction:: aioshad.crypto.generate_tmp_session
