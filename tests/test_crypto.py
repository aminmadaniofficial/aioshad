import pytest
from aioshad.crypto import (
    aes_decrypt,
    aes_encrypt,
    compute_sign,
    create_rsa_keys,
    decode_auth,
    decrypt_payload,
    decrypt_payload_probe,
    decrypt_rsa_oaep,
    derive_aes_key,
    derive_passphrase,
    derive_session_key,
    encrypt_payload,
    generate_tmp_session,
    rsa_sign,
)


def test_tmp_session_and_derive_passphrase():
    tmp = generate_tmp_session()
    assert len(tmp) == 32
    assert tmp.isalpha() and tmp.islower()

    passphrase = derive_passphrase(tmp)
    assert len(passphrase) == 32
    assert isinstance(passphrase, str)


def test_decode_auth():
    sample = "abcdefghijklmnopqrstuvwxyz0123456789"
    decoded = decode_auth(sample)
    assert len(decoded) == len(sample)
    assert decoded != sample


def test_aes_encrypt_decrypt():
    key = b"0123456789abcdef0123456789abcdef"  # 32 bytes
    plaintext = b"Hello, Shad Messenger! \xd8\xb3\xd9\x84\xd8\xa7\xd9\x85 \xd8\xb4\xd8\xa7\xd8\xaf"
    ciphertext = aes_encrypt(key, plaintext)
    assert ciphertext != plaintext

    recovered = aes_decrypt(key, ciphertext)
    assert recovered == plaintext


def test_encrypt_decrypt_payload():
    key = derive_aes_key("my_secret_key_123")
    plaintext = b'{"status":"OK","data":{"user_guid":"u0test"}}'
    data_enc = encrypt_payload(key, plaintext)
    assert isinstance(data_enc, str)

    decrypted = decrypt_payload(key, data_enc)
    assert decrypted == plaintext


def test_compute_sign():
    key = b"A" * 32
    data_enc = "c29tZV9kYXRh"
    sign = compute_sign(key, data_enc)
    assert isinstance(sign, str)
    assert len(sign) == 64  # SHA256 hex length


def test_rsa_key_generation_sign_decrypt():
    public_key_str, private_key_pem = create_rsa_keys()
    assert public_key_str
    assert "BEGIN PRIVATE KEY" in private_key_pem

    # Test signature
    data = "test_signing_payload"
    sig = rsa_sign(private_key_pem, data)
    assert sig
    assert isinstance(sig, str)


def test_decrypt_payload_probe():
    tmp_session = generate_tmp_session()
    key = derive_session_key(tmp_session)
    plaintext = b'{"probe":"success"}'
    data_enc = encrypt_payload(key, plaintext)

    decrypted, working_key, working_iv = decrypt_payload_probe(tmp_session, data_enc)
    assert decrypted == plaintext
    assert working_key == key
