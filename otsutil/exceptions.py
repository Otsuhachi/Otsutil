"""よく使う例外を纏めたモジュール。"""

__all__ = [
    "ObjectStoreError",
    "ObjectStoreLoadError",
    "ObjectStoreSaveError",
    "PathError",
    "PathTypeError",
]


class PathError(Exception):
    """パスに関連するエラー。"""


class PathTypeError(PathError):
    """パスの形式に関連するエラー。"""


class ObjectStoreError(Exception):
    """ObjectStore関連処理で発生する基底例外クラス。"""


class ObjectStoreSaveError(ObjectStoreError):
    """オブジェクトの保存（シリアライズ・書き込み）に失敗した際に送出される例外。"""


class ObjectStoreLoadError(ObjectStoreError):
    """オブジェクトの読み込み（でシリアライズ・読み込み）に失敗した際に送出される例外。"""
