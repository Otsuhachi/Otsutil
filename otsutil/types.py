"""よく使う型ヒントや定義を纏めたモジュールです。"""

__all__ = (
    "FLOAT_INT",
    "K",
    "P",
    "R",
    "T",
    "V",
    "hmsValue",
    "pathLike",
)


from pathlib import Path
from typing import ParamSpec, TypeVar

# タイプエイリアス
type hmsValue = tuple[int, int, float]
type pathLike = Path | str

# ジェネリクス
type FLOAT_INT = float | int

P = ParamSpec("P")
R = TypeVar("R")
K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")
