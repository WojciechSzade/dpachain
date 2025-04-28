import functools
import warnings
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA256
from Cryptodome.Signature import pss


def require_authorized(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.authorized:
            raise PermissionError(
                "This operation requires authorized blockchain service")
        return func(self, *args, **kwargs)
    return wrapper


def load_rsa_key(filename: str):
    if filename is None:
        warnings.error("No file key name provided")
        raise Exception("No file key name provided")
    with open("signing_keys/" + filename, "r") as key_file:
        return normalize_pem(key_file.read())


def normalize_pem(pem_str: str) -> str:
    # turn any literal “\n” sequences into real newlines
    pem_str = pem_str.replace("\\n", "\n")
    # strip leading/trailing whitespace
    pem_str = pem_str.strip()
    return pem_str


def validate_key_pair(private_key_pem: str, public_key_pem: str):
    priv = RSA.import_key(private_key_pem)
    pub_from_priv = priv.public_key()
    pub = RSA.import_key(public_key_pem)

    if pub_from_priv.n != pub.n:
        return False
    return True
