"""
otsutil - 汎用的なユーティリティパッケージ

このパッケージは、Python開発で頻繁に使用されるパス操作、ファイル入出力、
スレッドセーフなコレクション、タイマーなどの便利なツールを提供する。
"""

__all__ = [
    "JST",
    "__VERSION__",
    "ExpectType",
    "FloatInt",
    "HMSTuple",
    "LockableDict",
    "LockableList",
    "ObjectStore",
    "OptPath",
    "OptStrPath",
    "OtsuNone",
    "PathError",
    "PathTypeError",
    "StrPath",
    "Timer",
    "deduplicate",
    "get_sub_paths",
    "is_all_type",
    "is_dict_key_type",
    "is_dict_type",
    "is_dict_value_type",
    "is_type",
    "iter_sub_paths",
    "load_json",
    "read_lines",
    "same_path",
    "save_json",
    "setup_path",
    "str_to_path",
    "write_lines",
]


__VERSION__ = "1.3.2.312"

from .cfg import JST
from .classes import LockableDict, LockableList, ObjectStore, OtsuNone, Timer
from .exceptions import PathError, PathTypeError
from .funcs import (
    deduplicate,
    get_sub_paths,
    is_all_type,
    is_dict_key_type,
    is_dict_type,
    is_dict_value_type,
    is_type,
    iter_sub_paths,
    load_json,
    read_lines,
    same_path,
    save_json,
    setup_path,
    str_to_path,
    write_lines,
)
from .types import ExpectType, FloatInt, HMSTuple, OptPath, OptStrPath, StrPath
