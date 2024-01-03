import os
from os import urandom
import sys
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import cryptography.exceptions

# Ordnererstellung
directories = ["keys", "to_encrypt", "to_decrypt", "decrypted", "encrypted"]
for directory in directories:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Schlüsselerstellung (nur wenn noch nicht vorhanden)
private_key_path = "keys/private_key"
public_key_path = "keys/public_key"

if not os.path.exists(private_key_path) or not os.path.exists(public_key_path):
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    public_key = private_key.public_key()

    with open(private_key_path, 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open(public_key_path, 'wb') as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

def derive_key(private_key, public_key):
    shared_key = private_key.exchange(ec.ECDH(), public_key)
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake data',
        backend=default_backend()
    ).derive(shared_key)
    return derived_key

def encrypt_file(file_path, public_key):
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    derived_key = derive_key(private_key, public_key)

    # Generieren eines einzigartigen IVs
    iv = urandom(12)

    # AES Verschlüsselung mit GCM Modus
    cipher = Cipher(algorithms.AES(derived_key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    with open(file_path, 'rb') as f:
        plaintext = f.read()

    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    # Speichern von IV und verschlüsselten Daten
    encrypted_file_path = os.path.join('encrypted', os.path.basename(file_path))
    with open(encrypted_file_path, 'wb') as f:
        f.write(iv + ciphertext)  # IV wird vor den verschlüsselten Daten gespeichert


def decrypt_file(file_path, private_key):
    public_key = private_key.public_key()
    derived_key = derive_key(private_key, public_key)

    # Lesen der verschlüsselten Daten und des IVs
    with open(file_path, 'rb') as f:
        iv_ciphertext = f.read()
    iv = iv_ciphertext[:12]  # Die ersten 12 Bytes sind der IV
    ciphertext = iv_ciphertext[12:]

    # AES Entschlüsselung mit GCM Modus
    cipher = Cipher(algorithms.AES(derived_key), modes.GCM(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    try:
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
    except cryptography.exceptions.InvalidTag:
        print("Entschlüsselungsfehler: Ungültiger Tag")
        return

    # Speichern der entschlüsselten Datei
    decrypted_file_path = os.path.join('decrypted', os.path.basename(file_path))
    with open(decrypted_file_path, 'wb') as f:
        f.write(decrypted_data)

# Hauptlogik
if len(sys.argv) > 1:
    command = sys.argv[1]
    if command == "encrypt" and len(sys.argv) == 3:
        key_name = sys.argv[2]
        public_key_file = f"keys/{key_name}"
        if os.path.exists(public_key_file):
            with open(public_key_file, "rb") as f:
                public_key = serialization.load_pem_public_key(
                    f.read(),
                    backend=default_backend()
                )
            # Verschlüsseln aller Dateien im Ordner 'to_encrypt'
            for filename in os.listdir('to_encrypt'):
                file_path = os.path.join('to_encrypt', filename)
                if os.path.isfile(file_path):
                    encrypt_file(file_path, public_key)
                    # Verschieben der Datei nach 'encrypted'
                    os.rename(file_path, os.path.join('encrypted', filename))
        else:
            print(f"Öffentlicher Schlüssel '{key_name}' nicht gefunden.")
    elif command == "decrypt":
        # Implementierung der Entschlüsselungslogik
        pass
    else:
        print("Ungültiger Befehl oder falsche Parameter.")
else:
    print("Keine Befehle angegeben.")

