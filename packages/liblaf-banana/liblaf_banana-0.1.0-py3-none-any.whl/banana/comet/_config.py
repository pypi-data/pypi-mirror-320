import datetime
import secrets
from pathlib import Path

import comet_ml as comet
import pydantic
import pydantic_settings as ps

import banana as ba


def default_experiment_key() -> str:
    # https://www.comet.com/docs/v2/api-and-sdk/python-sdk/reference/start/
    # Must be an alphanumeric string whose length is between 32 and 50 characters.
    return secrets.token_hex(16)


def default_experiment_name() -> str:
    start_time: datetime.datetime = ba.start_time()
    return start_time.strftime("%Y-%m-%dT%H%M%S")


def default_project_name() -> str:
    config: comet.config.Config = comet.config.get_config()
    if project_name := comet.config.get_project_name(None, config):  # pyright: ignore[reportArgumentType]
        return project_name
    git_root: Path = ba.git.root()
    return git_root.name


def default_tags() -> list[str]:
    tags: list[str] = [ba.entrypoint().as_posix()]
    return tags


def default_workspace() -> str:
    config: comet.config.Config = comet.config.get_config()
    return comet.config.get_workspace(None, config)  # pyright: ignore[reportArgumentType]


class CometConfig(ps.BaseSettings):
    model_config = ps.SettingsConfigDict(env_prefix="BANANA_")
    enabled: bool = True
    experiment_key: str = pydantic.Field(default_factory=default_experiment_key)
    experiment_name: str = pydantic.Field(default_factory=default_experiment_name)
    project_name: str = pydantic.Field(default_factory=default_project_name)
    tags: list[str] = pydantic.Field(default_factory=default_tags)
    workspace: str = pydantic.Field(default_factory=default_workspace)

    @property
    def experiment_url(self) -> str:
        return f"https://www.comet.com/{self.workspace}/{self.project_name}/{self.experiment_key}"
