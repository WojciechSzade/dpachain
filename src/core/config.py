
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
    MONGODB_DB: str
    
    @computed_field
    @property
    def MONGODB_URL(self) -> str:
        return f"mongodb://{self.MONGODB_USER}:{self.MONGODB_PASSWORD}@{self.MONGODB_SERVER}:{self.MONGODB_PORT}"
        return MongoDsn.build(
            scheme="mongodb",
            username=self.MONGODB_USER,
            password=self.MONGODB_PASSWORD,
            host=self.MONGODB_SERVER,
            port=self.MONGODB_PORT,
            path=self.MONGODB_DB,
        )
    
settings = Settings()