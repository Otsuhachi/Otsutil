"""よく使う例外を纏めたモジュール。"""

__all__ = ["PathError", "PathTypeError"]


class PathError(Exception):
    """パスに関連するエラー。"""


class PathTypeError(Exception):
    """パスの形式に関連するエラー。"""
