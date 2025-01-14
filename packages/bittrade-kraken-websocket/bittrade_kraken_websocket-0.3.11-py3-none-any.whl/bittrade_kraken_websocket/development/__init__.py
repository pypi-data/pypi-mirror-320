from typing import List, Any

from reactivex import Observer, operators
from reactivex.abc import DisposableBase
from reactivex.disposable import CompositeDisposable, Disposable
from logging import getLogger
import traceback
import sys

logger = getLogger(__name__)
console = None
try:
    from rich.console import Console

    console = Console()
except ImportError:
    logger.warning("Package `rich` not installed. Some features may not work.")


def debug_observer(prefix: str) -> Observer[Any]:
    def fn(x, scope):
        logger.debug(f"[{prefix}][{scope}] - {x}")
        if scope == "ERROR":
            traceback.print_exception(*sys.exc_info())
            # if console:
            #     console.print_exception()

    return Observer(
        lambda x: fn(x, "NEXT"),
        lambda x: fn(x, "ERROR"),
        lambda: fn("No message on completion", "COMPLETE"),
    )


def debug_operator(prefix: str):
    return operators.do(debug_observer(prefix))


def info_observer(prefix: str) -> Observer[Any]:
    def fn(x, scope):
        logger.info(f"[{prefix}][{scope}] - {x}")
        if scope == "ERROR":
            traceback.print_exception(*sys.exc_info())
            # if console:
            #     console.print_exception()

    return Observer(
        lambda x: fn(x, "NEXT"),
        lambda x: fn(x, "ERROR"),
        lambda: fn("No message on completion", "COMPLETE"),
    )


def info_operator(prefix: str):
    return operators.do(info_observer(prefix))


class LogOnDisposeDisposable(CompositeDisposable):
    def __init__(self, disposables: List[DisposableBase], message: str = ""):
        super().__init__(
            *disposables,
            Disposable(action=lambda: logger.info("DISPOSING %s", message)),
        )
