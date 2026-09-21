from __future__ import annotations

import base64
import hashlib
import logging
import os
import secrets
import string
from typing import Final, Optional, Tuple, List

from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers import Cipher, modes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.backends import default_backend

_AES_BLOCK_SIZE: Final[int] = 16
_AES_KEY_BITS: Final[int] = 256
_IV: Final[bytes] = b"\x00" * _AES_BLOCK_SIZE
_BACKEND = default_backend()

logger = logging.getLogger("aioshad.crypto")


def derive_passphrase(auth: str) -> str:
    """
    Derives passphrase key from a 32-character string by transposing chunks
    and applying a modular shift on characters.
    """
    if len(auth) != 32:
        raise ValueError(f"auth length should be 32 characters, got {len(auth)}")
    chunks = [auth[i : i + 8] for i in range(0, 32, 8)]
    result_list = []
    for character in chunks[2] + chunks[0] + chunks[3] + chunks[1]:
        result_list.append(chr(((ord(character) - 97 + 9) % 26) + 97))
    return "".join(result_list)


def decode_auth(auth: str) -> str:
    """
    Decodes an auth token or RSA public key string using character translation.
    """
    result_list = []
    digits = "0123456789"
    translation_table_lower = str.maketrans(
        string.ascii_lowercase,
        "".join([chr(((32 - (ord(c) - 97)) % 26) + 97) for c in string.ascii_lowercase]),
    )
    translation_table_upper = str.maketrans(
        string.ascii_uppercase,
        "".join([chr(((29 - (ord(c) - 65)) % 26) + 65) for c in string.ascii_uppercase]),
    )
    for char in auth:
        if char in string.ascii_lowercase:
            result_list.append(char.translate(translation_table_lower))
        elif char in string.ascii_uppercase:
            result_list.append(char.translate(translation_table_upper))
        elif char in digits:
            result_list.append(chr(((13 - (ord(char) - 48)) % 10) + 48))
        else:
            result_list.append(char)
    return "".join(result_list)


def create_rsa_keys() -> Tuple[str, str]:
    """
    Generates a 1024-bit RSA key pair.
    Returns (public_key_str, private_key_pem).
    """
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=1024)
    pub_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    pub_b64 = base64.b64encode(pub_bytes).decode("utf-8")
    public_key_str = decode_auth(pub_b64)
    priv_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return public_key_str, priv_bytes.decode("utf-8")


def decrypt_rsa_oaep(private_key_pem: str, data: str) -> str:
    """
    Decrypts base64-encoded ciphertext using RSA OAEP SHA1.
    """
    from cryptography.hazmat.primitives.asymmetric import padding as asym_padding, rsa
    from cryptography.hazmat.primitives import hashes, serialization

    private_key = serialization.load_pem_private_key(
        private_key_pem.encode("utf-8"), password=None
    )
    if not isinstance(private_key, rsa.RSAPrivateKey):
        raise TypeError("Expected an RSA private key")
    decrypted = private_key.decrypt(
        base64.b64decode(data),
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA1(),
            label=None,
        ),
    )
    return decrypted.decode("utf-8")


def rsa_sign(private_key_pem: str, data: str) -> str:
    """
    Signs data using RSA PKCS1v15 and SHA256.
    Returns base64 signature string.
    """
    from cryptography.hazmat.primitives.asymmetric import padding as asym_padding, rsa
    from cryptography.hazmat.primitives import hashes, serialization

    private_key = serialization.load_pem_private_key(
        private_key_pem.encode("utf-8"), password=None
    )
    if not isinstance(private_key, rsa.RSAPrivateKey):
        raise TypeError("Expected an RSA private key")
    signature = private_key.sign(
        data.encode("utf-8"),
        asym_padding.PKCS1v15(),
        hashes.SHA256(),
    )
    return base64.b64encode(signature).decode("utf-8")


def derive_aes_key(raw_key: str) -> bytes:
    """Derives a 256-bit AES key using SHA256 of raw key string."""
    return hashlib.sha256(raw_key.encode()).digest()


def pkcs7_pad(data: bytes) -> bytes:
    """Applies PKCS7 padding to match AES block size."""
    padder = sym_padding.PKCS7(_AES_BLOCK_SIZE * 8).padder()
    return padder.update(data) + padder.finalize()


def pkcs7_unpad(data: bytes) -> bytes:
    """Removes PKCS7 padding."""
    unpadder = sym_padding.PKCS7(_AES_BLOCK_SIZE * 8).unpadder()
    return unpadder.update(data) + unpadder.finalize()


def aes_encrypt(key: bytes, plaintext: bytes, iv: bytes = _IV) -> bytes:
    """Encrypts plaintext bytes using AES CBC mode with PKCS7 padding."""
    cipher = Cipher(AES(key), modes.CBC(iv), backend=_BACKEND)
    encryptor = cipher.encryptor()
    padded = pkcs7_pad(plaintext)
    return encryptor.update(padded) + encryptor.finalize()


def aes_decrypt(key: bytes, ciphertext: bytes, iv: bytes = _IV) -> bytes:
    """Decrypts ciphertext bytes using AES CBC mode and unpads PKCS7."""
    cipher = Cipher(AES(key), modes.CBC(iv), backend=_BACKEND)
    decryptor = cipher.decryptor()
    padded_plain = decryptor.update(ciphertext) + decryptor.finalize()
    return pkcs7_unpad(padded_plain)


def encode_b64(data: bytes) -> str:
    """Encodes bytes to base64 string."""
    return base64.b64encode(data).decode("utf-8")


def decode_b64(data: str) -> bytes:
    """Decodes base64 string to bytes."""
    return base64.b64decode(data)


def encrypt_payload(key: bytes, plaintext: bytes, iv: bytes = _IV) -> str:
    """Encrypts plaintext bytes and returns base64 ciphertext string."""
    ciphertext = aes_encrypt(key, plaintext, iv)
    return encode_b64(ciphertext)


def decrypt_payload(key: bytes, data_enc: str, iv: bytes = _IV) -> bytes:
    """Decrypts base64-encoded encrypted payload into plaintext bytes."""
    ciphertext = decode_b64(data_enc)
    return aes_decrypt(key, ciphertext, iv)


def compute_sign(key: bytes, data_enc: str) -> str:
    """Computes SHA-256 signature from data_enc + base64(key)."""
    raw = data_enc + encode_b64(key)
    return hashlib.sha256(raw.encode()).hexdigest()


def generate_random_key(length: int = 32) -> bytes:
    """Generates random secure bytes."""
    return os.urandom(length)


def generate_tmp_session() -> str:
    """Generates random 32-character lowercase string for tmp_session."""
    return "".join(secrets.choice(string.ascii_lowercase) for _ in range(32))


def derive_session_key(tmp_session: str) -> bytes:
    """Derives session key by running derive_passphrase and encoding as utf-8."""
    return derive_passphrase(tmp_session).encode("utf-8")


def _candidate_key_iv_pairs(tmp_session: str) -> List[Tuple[bytes, bytes, str]]:
    passphrase_key = derive_passphrase(tmp_session).encode("utf-8")
    raw = tmp_session.encode("utf-8")
    sha = hashlib.sha256(raw).digest()
    zero_iv = b"\x00" * _AES_BLOCK_SIZE
    ascii_iv = b"0" * _AES_BLOCK_SIZE
    return [
        (passphrase_key, zero_iv, "key=passphrase(ts), iv=null_zeros"),
        (passphrase_key, ascii_iv, "key=passphrase(ts), iv=ascii_zeros"),
        (raw, zero_iv, "key=ts.utf8[32], iv=null_zeros"),
        (raw, ascii_iv, "key=ts.utf8[32], iv=ascii_zeros"),
        (sha, zero_iv, "key=sha256(ts), iv=null_zeros"),
        (sha, ascii_iv, "key=sha256(ts), iv=ascii_zeros"),
    ]


def decrypt_payload_probe(
    tmp_session: str, data_enc: str
) -> Tuple[bytes, bytes, bytes]:
    """
    Exhaustively attempts candidate key/IV combinations to decrypt a payload.
    Returns (plaintext, working_key, working_iv).
    """
    ciphertext = decode_b64(data_enc)
    for key, iv, label in _candidate_key_iv_pairs(tmp_session):
        if len(key) not in (16, 24, 32):
            continue
        try:
            cipher = Cipher(AES(key), modes.CBC(iv), backend=_BACKEND)
            decryptor = cipher.decryptor()
            padded = decryptor.update(ciphertext) + decryptor.finalize()
            plaintext = pkcs7_unpad(padded)
            logger.info("Successful decryption with derivation strategy: [%s]", label)
            return plaintext, key, iv
        except Exception as exc:
            logger.debug("Derivation strategy [%s] failed: %s", label, exc)

    raise ValueError(
        "All key/IV derivation strategies exhausted. "
        "Server response cannot be decrypted. The protocol may have changed."
    )
