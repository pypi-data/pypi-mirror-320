from __future__ import annotations
from time import perf_counter
from typing import Any, Callable, Optional

from .log import getLogger

__all__ = [
    "MeasureTime",
]


class MeasureTime:
    def __init__(
        self,
        func: Optional[Callable] = None,
        *,
        mute: bool = False,
    ) -> None:
        self.logger = getLogger()
        self.func = func
        self.mute = mute
        self._used = None

    def info(self, *args, **kwargs) -> None:
        if not self.mute:
            self.logger.info(*args, **kwargs)

    def __call__(self, *args, **kwargs) -> Any:
        if self.func is None:
            raise ValueError("No function provided")
        start_time = perf_counter()
        error = None
        try:
            result = self.func(*args, **kwargs)
        except Exception as e:
            error = e
        end_time = perf_counter()
        self.info(
            f"Procedure {self.func.__name__!r} took {end_time - start_time} seconds to run"
        )
        if error:
            raise error
        return result

    def __enter__(self) -> MeasureTime:
        self.start = perf_counter()
        return self

    def __exit__(self, *args, **kwargs) -> None:
        self.done()
        self.info(f"Program took {self.used} seconds to run")

    @property
    def used(self) -> float:
        if self._used is None:
            return self.done()
        return self._used

    def init(self) -> None:
        self.start = perf_counter()
        self.end = None
        self._used = None

    def done(self) -> float:
        self.end = perf_counter()
        self._used = self.end - self.start
        return self.used
