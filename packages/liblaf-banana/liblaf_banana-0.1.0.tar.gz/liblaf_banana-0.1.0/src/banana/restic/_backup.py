import os
import subprocess as sp

from loguru import logger

import banana as ba


def backup(config: ba.restic.ResticConfig) -> bool:
    if not config.enabled:
        return False
    if not config.config.exists():
        logger.warning("configuration file '{}' was not found", config.config)
        return False
    args: list[str | os.PathLike[str]] = [
        "resticprofile",
        "--config",
        config.config,
        "backup",
    ]
    if config.name:
        args += ["--name", config.name]
    if config.dry_run:
        args.append("--dry-run")
    if config.time:
        args += ["--time", config.time.strftime("%Y-%m-%d %H:%M:%S")]
    proc: sp.CompletedProcess[bytes] = sp.run(args, check=False)
    return proc.returncode == 0
