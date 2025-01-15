from typing import Optional, Callable
import logging

try:
    from rich.logging import RichHandler

    _format = "%(message)s"
    _datefmt = None
    _handlers = [
        RichHandler(
            show_level=True,
            show_path=False,
            log_time_format="%H:%M:%S",
            omit_repeated_times=False,
        )
    ]
except ImportError:
    _format = "%(asctime)s  %(levelname)s    %(message)s"
    _datefmt = "%H:%M:%S"
    _handlers = None

__all__ = [
    "getLogger",
]


class MutToneLogger:
    method_map = {
        "log": "log",
        "debug": "debug",
        "info": "info",
        "warning": "warning",
        "error": "error",
        "critical": "critical",
        "exception": "exception",
    }

    def __init__(self, logger: logging.Logger, mute: bool = False) -> None:
        self.logger = logger
        self.mute = mute

    def mute_all(self, *args, **kwargs) -> None:
        pass

    def __getattr__(self, name: str) -> Callable:
        if name in self.method_map:
            if self.mute:
                return self.mute_all
            return getattr(self.logger, self.method_map[name])
        raise AttributeError(f"No such method: {name}")


def getLogger(name: Optional[str] = None, *, mute: bool = False) -> "MutToneLogger":
    logging.basicConfig(
        format=_format,
        datefmt=_datefmt,
        level=logging.INFO,
        handlers=_handlers,
    )
    logger = logging.getLogger(name)
    return MutToneLogger(logger, mute)
