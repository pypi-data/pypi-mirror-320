import comet_ml  # noqa: ICN001

import banana as ba


def start(
    *, auto_commit: bool | None = None, comet: ba.comet.CometConfig | None = None
) -> comet_ml.CometExperiment:
    if comet is None:
        comet = ba.comet.CometConfig()
    if auto_commit is True or comet.enabled:
        ba.git.auto_commit(
            f"""\
chore(exp): auto commit

name : {comet.experiment_name}
url  : {comet.experiment_url}\
    """
        )
    exp: comet_ml.CometExperiment = comet_ml.start(
        workspace=comet.workspace,
        project_name=comet.project_name,
        experiment_key=comet.experiment_key,
        experiment_config=comet_ml.ExperimentConfig(
            disabled=not comet.enabled,
            name=comet.experiment_name,
            tags=comet.tags,
        ),
    )
    return exp
