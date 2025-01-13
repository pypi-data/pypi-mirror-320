from __future__ import annotations

from pathlib import Path
from importlib import metadata

from pydantic import field_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_core.core_schema import ValidationInfo

from ethosian.utils.log import logger

ethosian_cli_DIR: Path = Path.home().resolve().joinpath(".ethosian")


class ethosianCliSettings(BaseSettings):
    app_name: str = "ethosian"
    app_version: str = metadata.version("ethosian")

    tmp_token_path: Path = ethosian_cli_DIR.joinpath("tmp_token")
    config_file_path: Path = ethosian_cli_DIR.joinpath("config.json")
    credentials_path: Path = ethosian_cli_DIR.joinpath("credentials.json")
    ai_conversations_path: Path = ethosian_cli_DIR.joinpath(
        "ai_conversations.json")
    auth_token_cookie: str = "__ethosian_session"
    auth_token_header: str = "X-ethosian-AUTH-TOKEN"

    api_runtime: str = "prd"
    api_enabled: bool = True
    alpha_features: bool = False
    api_url: str = Field("https://api.ethosian.com", validate_default=True)
    signin_url: str = Field(
        "https://ethosian.app/login", validate_default=True)
    playground_url: str = Field(
        "https://ethosian.app/playground", validate_default=True)

    model_config = SettingsConfigDict(env_prefix="ethosian_")

    @field_validator("api_runtime", mode="before")
    def validate_runtime_env(cls, v):
        """Validate api_runtime."""

        valid_api_runtimes = ["dev", "stg", "prd"]
        if v not in valid_api_runtimes:
            raise ValueError(f"Invalid api_runtime: {v}")

        return v

    @field_validator("signin_url", mode="before")
    def update_signin_url(cls, v, info: ValidationInfo):
        api_runtime = info.data["api_runtime"]
        if api_runtime == "dev":
            return "http://localhost:3000/login"
        elif api_runtime == "stg":
            return "https://stgethosian.com/login"
        else:
            return "https://ethosian.app/login"

    @field_validator("playground_url", mode="before")
    def update_playground_url(cls, v, info: ValidationInfo):
        api_runtime = info.data["api_runtime"]
        if api_runtime == "dev":
            return "http://localhost:3000/playground"
        elif api_runtime == "stg":
            return "https://stgethosian.com/playground"
        else:
            return "https://ethosian.app/playground"

    @field_validator("api_url", mode="before")
    def update_api_url(cls, v, info: ValidationInfo):
        api_runtime = info.data["api_runtime"]
        if api_runtime == "dev":
            from os import getenv

            if getenv("ethosian_RUNTIME") == "docker":
                return "http://host.docker.internal:7070"
            return "http://localhost:7070"
        elif api_runtime == "stg":
            return "https://api.stgethosian.com"
        else:
            return "https://api.ethosian.com"

    def gate_alpha_feature(self):
        if not self.alpha_features:
            logger.error(
                "This is an Alpha feature not for general use.\nPlease message the ethosian team for access.")
            exit(1)


ethosian_cli_settings = ethosianCliSettings()
