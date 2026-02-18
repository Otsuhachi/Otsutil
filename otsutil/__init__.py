"""
otsutil - 汎用的なユーティリティパッケージ

このパッケージは、Python開発で頻繁に使用されるパス操作、ファイル入出力、
スレッドセーフなコレクション、タイマーなどの便利なツールを提供します。
"""

from .classes import (
    LockableDict,
    LockableList,
    ObjectStore,
    OtsuNone,
    Timer,
)
from .funcs import (
    deduplicate,
    ensure_relative,
    get_sub_paths,
    get_value,
    is_all_type,
    is_type,
    load_json,
    read_lines,
    same_path,
    save_json,
    setup_path,
    str_to_path,
    write_lines,
)
from .types import (
    FloatInt,
    HMSTuple,
    K,
    P,
    R,
    StrPath,
    T,
    V,
)

__all__ = (
    "FloatInt",
    "K",
    "LockableDict",
    "LockableList",
    "ObjectStore",
    "OtsuNone",
    "P",
    "R",
    "T",
    "Timer",
    "V",
    "deduplicate",
    "ensure_relative",
    "get_sub_paths",
    "get_value",
    "HMSTuple",
    "is_all_type",
    "is_type",
    "load_json",
    "StrPath",
    "read_lines",
    "same_path",
    "save_json",
    "setup_path",
    "str_to_path",
    "write_lines",
)
__version__ = "1.3.0.312"
