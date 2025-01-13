import comet_ml as comet

import banana as ba


def end(*, restic: ba.restic.ResticConfig | None = None) -> None:
    exp: comet.CometExperiment | None = comet.get_running_experiment()
    if exp:
        if restic is None:
            restic = ba.restic.ResticConfig(enabled=not exp.disabled)
        ba.restic.backup(restic)
    comet.end()
