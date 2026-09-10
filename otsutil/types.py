"""よく使う型ヒントや定義を纏めたモジュール。"""

__all__ = [
    "ExpectType",
    "FloatInt",
    "HMSTuple",
    "OptPath",
    "OptStrPath",
    "StrPath",
]


import pathlib

type ExpectType[T] = type[T] | tuple[type[T], ...]
type FloatInt = float | int
type HMSTuple = tuple[int, int, float]
type OptPath = pathlib.Path | None
type OptStrPath = pathlib.Path | str | None
type StrPath = pathlib.Path | str
