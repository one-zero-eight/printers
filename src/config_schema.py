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
    display_name: str
    "Display name of the printer, it will be shown to the user"
    cups_name: str
    "Name of the printer in CUPS"
    ipp: str = Field(examples=["192.168.1.1", "host.docker.internal:62102", "127.0.0.1:62102"])
    "IP address of the printer for accessing IPP. Specify a port if it differs from 631."


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
    cups_server: str | None = Field(
        default=None,
        examples=["localhost", "cups", "127.0.0.1"],
    )
    "CUPS hostname, if None then /run/cups-socket/cups.sock will be used"
    cups_port: int = 631
    "CUPS port"
    cups_user: str | None = None
    "CUPS username, if None then current user will be used"
    cups_password: SecretStr | None = None
    "CUPS password"
    printers_list: list[Printer]
    "List of printers"
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

    schema_: str | None = Field(None, alias="$schema")
    api: ApiSettings = None  # type: ignore
    bot: BotSettings = None  # type: ignore

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
