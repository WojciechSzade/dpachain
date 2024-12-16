
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
        env_file="../.env",
    )
    PROJECT_NAME: str
    MONGODB_SERVER: str
    MONGODB_PORT: int = 27017
    MONGODB_USER: str
    MONGODB_PASSWORD: str
    P2P_PORT: int = 44666
    NODES_LIST_FILE: str = "nodes_list.txt"
    HOST_NODE_NAME: str = "host-" + secrets.token_hex(4)

    @computed_field
    @property
    def MONGODB_URL(self) -> str:
        return MongoDsn.build(
            scheme="mongodb",
            username=self.MONGODB_USER,
            password=self.MONGODB_PASSWORD,
            host=self.MONGODB_SERVER,
            port=self.MONGODB_PORT,
            path="",
        )


settings = Settings()
