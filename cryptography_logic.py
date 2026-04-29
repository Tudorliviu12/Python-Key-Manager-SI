import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.backends import default_backend

def criptare_python_aes(path_in, path_out, cheie_hex, iv_hex):
    key = bytes.fromhex(cheie_hex)
    iv = bytes.fromhex(iv_hex)
    padder = padding.PKCS7(128).padder()
    with open(path_in, 'rb') as f:
        plaintext = f.read()
    padded_data = padder.update(plaintext) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    with open(path_out, "wb") as f:
        f.write(ciphertext)


def decriptare_python_aes(path_in, path_out, cheie_hex, iv_hex):
    key = bytes.fromhex(cheie_hex)
    iv = bytes.fromhex(iv_hex)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    with open(path_in, "rb") as f:
        ciphertext = f.read()

    padded_data = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_data) + unpadder.finalize()

    with open(path_out, "wb") as f:
        f.write(plaintext)


def criptare_python_rsa(path_in, path_out, nume_fisier_public):
    with open(nume_fisier_public, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )

    with open(path_in, "rb") as f:
        plaintext = f.read()

    ciphertext = public_key.encrypt(plaintext, asym_padding.PKCS1v15())

    with open(path_out, "wb") as f:
        f.write(ciphertext)


def decriptare_python_rsa(path_in, path_out, nume_fisier_privat):
    with open(nume_fisier_privat, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

    with open(path_in, "rb") as f:
        ciphertext = f.read()

    plaintext = private_key.decrypt(ciphertext, asym_padding.PKCS1v15())

    with open(path_out, "wb") as f:
        f.write(plaintext)