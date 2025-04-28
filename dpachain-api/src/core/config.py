
import os
import secrets
from typing import Any


from pydantic import (
    MongoDsn,
    computed_field,
)

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_core import MultiHostUrl
from src.utils.utils import load_rsa_key, validate_key_pair


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
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
    SIGNING_KEY_FILE_NAME: str
    GENERATING_KEY_FILE_NAME: str | None = None
    GENESIS_KEYS_FILE: str | None = None
    UNIVERSITY_NAME: str | None = None

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
        return load_rsa_key(self.SIGNING_KEY_FILE_NAME + ".pem")

    @computed_field
    def SIGNING_PUBLIC_KEY(self) -> str:
        return load_rsa_key(self.SIGNING_KEY_FILE_NAME + ".pub")

    @computed_field
    def GENERATING_PRIVATE_KEY(self) -> str | None:
        if self.GENERATING_KEY_FILE_NAME:
            return load_rsa_key(self.GENERATING_KEY_FILE_NAME + ".pem")
        return None

    @computed_field
    def GENERATING_PUBLIC_KEY(self) -> str | None:
        if self.GENERATING_KEY_FILE_NAME:
            return load_rsa_key(self.GENERATING_KEY_FILE_NAME + ".pub")
        return None

    def model_post_init(self, __context: Any) -> None:
        assert self.NETWORK_ID is not None and self.NETWORK_ID != "", "NETWORK_ID must be set"
        assert self.CHAIN_VERSION is not None and self.CHAIN_VERSION != "", "CHAIN_VERSION must be set"
        assert validate_key_pair(
            self.SIGNING_PRIVATE_KEY, self.SIGNING_PUBLIC_KEY), "Invalid signing key - key pair doesn't match"
        if self.AUTHORIZED:
            assert self.GENERATING_PUBLIC_KEY is not None, "Public generating key was not provided."
            assert self.GENERATING_PRIVATE_KEY is not None, "Private generating key was not provided."
            assert validate_key_pair(
                self.GENERATING_PRIVATE_KEY, self.GENERATING_PUBLIC_KEY), "Invalid generating key - key pair doesn't match"
            assert self.UNIVERSITY_NAME


settings = Settings()
