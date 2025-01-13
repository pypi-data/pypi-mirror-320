import datetime
from pathlib import Path

import pydantic
import pydantic_settings as ps

import banana as ba


def default_config() -> Path:
    git_root: Path = ba.git.root()
    for config in [
        git_root / ".config" / "resticprofile.toml",
        git_root / "resticprofile.toml",
    ]:
        if config.exists():
            return config
    return git_root / ".config" / "resticprofile.toml"


class ResticConfig(ps.BaseSettings):
    model_config = ps.SettingsConfigDict(env_prefix="BANANA_RESTIC_")
    enabled: bool = True
    config: Path = pydantic.Field(default_factory=default_config)
    dry_run: bool = False
    name: str | None = None
    time: datetime.datetime = pydantic.Field(default_factory=ba.start_time)
