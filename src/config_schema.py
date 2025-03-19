from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict, YamlConfigSettingsSource


class Environment(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class SettingBaseModel(BaseSettings):
    model_config = SettingsConfigDict(use_attribute_docstrings=True, extra="forbid", env_file=".env")


class Settings(SettingBaseModel):
    """Settings for the application."""

    schema_: str | None = Field(None, alias="$schema")
    environment: Environment = Environment.DEVELOPMENT
    "App environment flag"
    app_root_path: str = ""
    'Prefix for the API path (e.g. "/api/v0")'
    database_uri: SecretStr = Field(
        examples=[
            "mongodb://mongoadmin:secret@localhost:27017/db?authSource=admin",
            "mongodb://mongoadmin:secret@db:27017/db?authSource=admin",
        ]
    )
    "MongoDB database settings"
    cors_allow_origin_regex: str = ".*"
    "Allowed origins for CORS: from which domains requests to the API are allowed. Specify as a regex: `https://.*.innohassle.ru`"
    cups_server_host: str = "127.0.0.1"
    "CUPS server host"
    cups_server_port: int = 631
    "CUPS server port"
    """InNoHassle Accounts integration settings"""
    cups_server_admin_user: str = "admin"
    "CUPS server admin user"
    cups_server_admin_password: SecretStr | None = None
    innohassle_api_url: str = "https://api.innohassle.ru/accounts/v0"
    "URL of the Accounts API"
    innohassle_api_jwt_token: SecretStr
    "JWT token for accessing the Accounts API as a service"

    @classmethod
    def save_schema(cls, path: Path) -> None:
        with open(path, "w") as f:
            schema = {"$schema": "https://json-schema.org/draft-07/schema", **cls.model_json_schema()}
            yaml.dump(schema, f, sort_keys=False)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        yaml_settings = YamlConfigSettingsSource(
            settings_cls,
            Path("settings.yaml"),
        )
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            yaml_settings,
        )
