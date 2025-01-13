import functools
import inspect
from collections.abc import Callable
from typing import ParamSpec, TypeVar

import comet_ml  # noqa: ICN001

import banana as ba

_P = ParamSpec("_P")
_T = TypeVar("_T")


def main(
    *,
    config: ba.BaseConfig | None = None,
    comet: ba.comet.CometConfig | None = None,
    restic: ba.restic.ResticConfig | None = None,
) -> Callable[[Callable[_P, _T]], Callable[_P, _T]]:
    def wrapper(fn: Callable[_P, _T]) -> Callable[_P, _T]:
        @functools.wraps(fn)
        def wrapped(*args: _P.args, **kwargs: _P.kwargs) -> _T:
            exp: comet_ml.CometExperiment = ba.start(comet=comet)
            sig: inspect.Signature = inspect.signature(fn)
            bound_args: inspect.BoundArguments = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            for key in ["e", "exp", "experiment"]:
                if key in sig.parameters:
                    bound_args.arguments[key] = exp
            for key in ["c", "cfg", "config", "configuration"]:
                if key in sig.parameters:
                    bound_args.arguments[key] = config
            result: _T = fn(*bound_args.args, **bound_args.kwargs)
            ba.end(restic=restic)
            return result

        return wrapped

    return wrapper
