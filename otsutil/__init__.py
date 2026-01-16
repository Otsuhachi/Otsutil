"""
otsutil - 汎用的なユーティリティパッケージ

このパッケージは、Python開発で頻繁に使用されるパス操作、ファイル入出力、
スレッドセーフなコレクション、タイマーなどの便利なツールを提供します。
"""

from .classes import (
    LockableDict,
    LockableList,
    ObjectSaver,
    OtsuNone,
    Timer,
)
from .funcs import (
    deduplicate,
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
    FLOAT_INT,
    K,
    P,
    R,
    T,
    V,
    hmsValue,
    pathLike,
)

__all__ = (
    "FLOAT_INT",
    "K",
    "LockableDict",
    "LockableList",
    "ObjectSaver",
    "OtsuNone",
    "P",
    "R",
    "T",
    "Timer",
    "V",
    "deduplicate",
    "get_value",
    "hmsValue",
    "is_all_type",
    "is_type",
    "load_json",
    "pathLike",
    "read_lines",
    "same_path",
    "save_json",
    "setup_path",
    "str_to_path",
    "write_lines",
)
__version__ = "1.2.3.312"
