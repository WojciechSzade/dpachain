import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

universities = [
    "Politechnika Warszawska",
    "Politechnika Gdańska",
    "Uniwersytet Warszawski",
    "Uniwersytet Gdański",
    "Akademia Górniczo-Hutnicza",
    "Uniwersytet Jagielloński",
    "Politechnika Wrocławska",
    "Uniwersytet Wrocławski"
]

keys_data = {}


for uni in universities:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    keys_data[uni] = {
        "private_key": private_pem,
        "public_key": public_pem
    }

file_path = "./authenticated_keys.json"
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(keys_data, f, ensure_ascii=False, indent=2)
