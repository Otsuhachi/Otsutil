"""よく使う型ヒントや定義を纏めたモジュールです。"""

__all__ = (
    "FloatInt",
    "K",
    "P",
    "R",
    "T",
    "V",
    "HMSTuple",
    "StrPath",
)


from pathlib import Path
from typing import ParamSpec, TypeVar

# タイプエイリアス
type HMSTuple = tuple[int, int, float]
type StrPath = Path | str

# ジェネリクス
type FloatInt = float | int

P = ParamSpec("P")
R = TypeVar("R")
K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")
