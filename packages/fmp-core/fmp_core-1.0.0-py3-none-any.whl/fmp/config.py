"""
Configuration module.

This module contains configuration classes and settings for the application.
It includes configurations for MongoDB, APIs, paths, proxies etc.
"""

from datetime import UTC, timezone
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class MongoDBConfig(BaseSettings):
    """
    MongoDB configuration class.

    Attributes
    ----------
    host : str
        The hostname of the MongoDB server.
    port : int
        The port number on which the MongoDB server is listening.
    db_name : str
        The name of the MongoDB database.
    user : Optional[str]
        The username for MongoDB authentication.
    password : Optional[str]
        The password for MongoDB authentication.
    """

    host: str = "localhost"
    port: int = 27017
    db_name: str
    user: Optional[str]
    password: Optional[str]

    @property
    def url(self) -> str:
        """
        Returns the MongoDB connection URL.

        Returns
        -------
        str
            The MongoDB connection URL.
        """
        auth = f"{self.user}:{self.password}@" if self.user else ""
        return f"mongodb://{auth}{self.host}:{self.port}/{self.db_name}"


class Config(BaseSettings):
    """
    Application configuration class.

    Attributes
    ----------
    mongodb : MongoDBConfig
        MongoDB configuration.
    project_path : PathConfig
        Project paths configuration.
    fmp : FMPConfig
        Forex defaults/setup configuration.
    proxy : ProxyConfig
        Proxy configuration - dynamic/static.
    model_config : SettingsConfigDict
        Pydantic model configuration.
    """

    mongodb: MongoDBConfig

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        case_sensitive=False,
        env_file=".env",
        extra="allow",
    )

    @property
    def timezone(self) -> timezone:
        """
        Returns the timezone.

        Returns
        -------
        timezone
            Timezone.
        """
        return UTC


cfg = Config()  # noqa
