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
    ipp: str = Field(examples=["192.168.1.1:631", "host.docker.internal:62102", "127.0.0.1:62102"])
    "IP address of the printer for accessing IPP. Always specify a port."


class Scanner(SettingBaseModel):
    display_name: str
    "Display name of the scanner, it will be shown to the user"
    name: str
    "Identifier of the scanner for the application"
    escl: str = Field(examples=["https://192.168.1.1:9096/eSCL", "https://host.docker.internal:50001/eSCL"])
    "ESCL base url"


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
    scanners_list: list[Scanner]
    "List of scanners"
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
    database_uri: SecretStr = Field(
        examples=[
            "mongodb://mongoadmin:secret@localhost:27017/db?authSource=admin",
            "mongodb://mongoadmin:secret@db:27017/db?authSource=admin",
        ]
    )
    "MongoDB database settings for FSM"
    database_db_name: str = "db"
    "MongoDB database name for FSM"
    database_collection_name: str = "aiogram_fsm"
    "MongoDB collection name for FSM"
    help_video_id: str | None = None
    "ID of the video to send as help message"


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
