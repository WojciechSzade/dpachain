
import secrets
import warnings

from pydantic import (
    MongoDsn,
    computed_field,
)

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_core import MultiHostUrl


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
    )
    PROJECT_NAME: str
    MONGODB_SERVER: str
    MONGODB_PORT: int = 27017
    MONGODB_USER: str
    MONGODB_PASSWORD: str
    P2P_PORT: int = 44666
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    NODES_LIST_FILE: str = "nodes_list.txt"
    HOST_NODE_NAME: str = "host_node" + secrets.token_hex(4)
    DEBUG: bool = False
    NETWORK_ID: str
    CHAIN_VERSION: str
    AUTHORIZED: bool = False
    SIGNING_KEY_NAME: str

    @computed_field
    def MONGODB_URL(self) -> str:
        return str(MongoDsn.build(
            scheme="mongodb",
            username=self.MONGODB_USER,
            password=self.MONGODB_PASSWORD,
            host=self.MONGODB_SERVER,
            port=self.MONGODB_PORT,
            path="",
        ))

    @computed_field
    def SIGNING_PRIVATE_KEY(self) -> str:
        if self.SIGNING_KEY_NAME is None:
            warnings.error("No signing key name provided")
            raise Exception("No signing key name provided")
        with open("signing_keys/" + self.SIGNING_KEY_NAME, "r") as private_key_file:
            return private_key_file.read()

    @computed_field
    def SIGNING_PUBLIC_KEY(self) -> str:
        if self.SIGNING_KEY_NAME is None:
            warnings.error("No signing key name provided")
            raise Exception("No signing key name provided")
        with open("signing_keys/" + self.SIGNING_KEY_NAME + ".pub", "r") as public_key_file:
            return public_key_file.read()


settings = Settings()
