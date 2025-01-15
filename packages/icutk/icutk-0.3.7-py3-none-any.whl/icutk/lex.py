from __future__ import annotations
from io import TextIOWrapper
from typing import Iterator, Optional, Union, Any

from ply.lex import (
    LexToken as _LexToken,
    Lexer,
    TOKEN,
    lex,
)


__all__ = [
    "TOKEN",
    "LexToken",
    "Lexer",
    "MetaLexer",
    "BaseLexer",
]


class LexToken(_LexToken):
    lexer: Lexer
    type: str
    value: Any
    lineno: int
    lexpos: int


class MetaLexer:
    def __new__(cls, *args, **kwargs):
        if cls is MetaLexer:
            raise TypeError("BaseLexer cannot be instantiated")
        return super().__new__(cls)

    t_ignore = " \t"

    def t_error(self, t):
        t.lexer.skip(1)

    def __init__(self) -> None:
        self.lexer = lex(module=self, debug=False)

    def input(self, data: Union[str, TextIOWrapper]):
        if isinstance(data, str):
            pass
        elif isinstance(data, TextIOWrapper):
            data = data.read()
        else:
            raise TypeError(f"data must be str or TextIOWrapper - {data!r}")
        self.lexer.input(data)

    def token(self) -> Optional[LexToken]:
        return self.lexer.token()

    def line_count(self, s: str) -> None:
        self.lexer.lineno += s.count("\n")

    def __iter__(self) -> Iterator[LexToken]:
        return self

    def __next__(self) -> LexToken:
        t = self.token()
        if t is None:
            raise StopIteration
        return t


class BaseLexer(MetaLexer):
    tokens = [
        "ID",  # abc
        "FLOAT",  # 1.23
        "INT",  # 10
    ]

    literals = """()[]{}<>+-*/=~!@#$%^&\\|;:'",.?_"""

    def __init__(self, data: Optional[str] = None) -> None:
        super().__init__()
        if data is not None:
            self.input(data)

    def t_ID(self, t: LexToken):
        r"[a-zA-Z_]\w*"
        return t

    def t_FLOAT(self, t: LexToken):
        r"\d+\.\d+"
        t.value = float(t.value)
        return t

    def t_INT(self, t: LexToken):
        r"\d+(?!\.)"
        t.value = int(t.value)
        return t

    def t_newline(self, t: LexToken):
        r"\n+"
        self.line_count(t.value)
