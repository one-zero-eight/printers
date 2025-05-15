from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, SecretStr


class Environment(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class SettingBaseModel(BaseModel):
    model_config = ConfigDict(use_attribute_docstrings=True, extra="forbid")


class Printer(SettingBaseModel):
    name: str
    cups_name: str
    ip: str


class Accounts(SettingBaseModel):
    """InNoHassle Accounts integration settings"""

    api_url: str = "https://api.innohassle.ru/accounts/v0"
    "URL of the Accounts API"
    api_jwt_token: SecretStr
    "JWT token for accessing the Accounts API as a service"


class ApiSettings(SettingBaseModel):
    app_root_path: str = ""
    'Prefix for the API path (e.g. "/api/v0")'
    database_uri: SecretStr = Field(
        examples=[
            "mongodb://mongoadmin:secret@localhost:27017/db?authSource=admin",
            "mongodb://mongoadmin:secret@db:27017/db?authSource=admin",
        ]
    )
    "MongoDB database settings"
    unoserver_server: str = "127.0.0.1"
    "unoserver server network"
    unoserver_port: int = 2003
    "Unoserver server network port"
    cups_server: str | None = None  # default is /run/cups/cups.sock, but you can change to "localhost"
    "CUPS hostname"
    cups_port: int = 631
    "CUPS port"
    cups_user: str | None = None  # default is current user
    "CUPS username"
    cups_password: SecretStr | None = None
    "CUPS password"
    printers_list: list[Printer]
    cors_allow_origin_regex: str = ".*"
    "Allowed origins for CORS: from which domains requests to the API are allowed. Specify as a regex: `https://.*.innohassle.ru`"
    accounts: Accounts
    "InNoHassle Accounts integration settings"
    temp_dir: str = "./tmp"
    "Temporary directory to store converted and input files"


class BotSettings(SettingBaseModel):
    bot_token: SecretStr
    "Token from BotFather"
    api_url: str = "http://127.0.0.1:8000"
    "Print API url"


class Settings(SettingBaseModel):
    """Settings for the application."""

    schema_: str = Field(None, alias="$schema")
    api: ApiSettings | None = None
    bot: BotSettings | None = None

    @classmethod
    def from_yaml(cls, path: Path) -> "Settings":
        with open(path) as f:
            yaml_config = yaml.safe_load(f)

        return cls.model_validate(yaml_config)

    @classmethod
    def save_schema(cls, path: Path) -> None:
        with open(path, "w") as f:
            schema = {"$schema": "https://json-schema.org/draft-07/schema", **cls.model_json_schema()}
            yaml.dump(schema, f, sort_keys=False)
