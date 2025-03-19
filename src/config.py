import os

from src.config_schema import Settings

settings_path = os.getenv("SETTINGS_PATH", "settings.yaml")
settings: Settings = Settings()
