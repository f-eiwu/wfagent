from __future__ import annotations

from typing import TextIO


def write(stream: TextIO, text: str) -> None:
    stream.write(text)


def write_line(stream: TextIO, text: str = "") -> None:
    stream.write(text + "\n")
