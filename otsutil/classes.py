from __future__ import annotations

import asyncio
import base64
import os
import pickle
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from threading import RLock
from typing import TYPE_CHECKING, Any, Final, SupportsIndex, TypeGuard, overload

from .exceptions import ObjectStoreLoadError, PathTypeError
from .funcs import setup_path

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Callable, Iterable, Iterator
    from types import TracebackType

    from .types import HMSTuple, StrPath


"""よく使うクラスを纏めたモジュール。"""

__all__ = [
    "LockableDict",
    "LockableList",
    "ObjectStore",
    "OtsuNone",
    "OtsuNoneType",
    "Timer",
]


class OtsuNoneType:
    """異常なNoneを表すためのセンチネルクラス。"""

    __slots__ = ()

    def __repr__(self) -> str:
        return "OtsuNone"

    def __bool__(self) -> bool:
        return False

    def __copy__(self) -> OtsuNoneType:
        return OtsuNone

    def __deepcopy__(self, memo: Any) -> OtsuNoneType:
        return OtsuNone

    def __reduce__(self) -> str:
        return "OtsuNone"


OtsuNone: Final[OtsuNoneType] = OtsuNoneType()


class LockableDict[K, V](dict[K, V]):
    """要素の操作時にthreading.RLockを使用するスレッドセーフなdictクラス。

    個々のメソッド（get, pop, update等）は自動的にロックで保護されます。
    またwith構文を使用することで、複数の操作をアトミックに実行できます。
    RLockを使用しているため、同一スレッド内での再入（二重ロック）が可能です。
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """LockableDictを初期化する。"""
        super().__init__(*args, **kwargs)
        self._lock = RLock()

    def __contains__(self, key: object, /) -> bool:
        with self._lock:
            return super().__contains__(key)

    def __delitem__(self, key: K) -> None:
        with self._lock:
            super().__delitem__(key)

    def __getitem__(self, key: K) -> V:
        with self._lock:
            return super().__getitem__(key)

    def __setitem__(self, key: K, value: V) -> None:
        with self._lock:
            super().__setitem__(key, value)

    def __iter__(self) -> Iterator[K]:
        with self._lock:
            return iter(list(super().__iter__()))

    def __len__(self) -> int:
        with self._lock:
            return super().__len__()

    def __ior__(self, other: Any) -> LockableDict[K, V]:
        with self._lock:
            super().__ior__(other)
            return self

    def clear(self) -> None:
        with self._lock:
            super().clear()

    def copy(self) -> LockableDict[K, V]:
        with self._lock:
            return LockableDict(super().copy())

    def get(self, key: K, default: Any = None) -> Any:
        with self._lock:
            return super().get(key, default)

    def items(self) -> Any:
        with self._lock:
            return list(super().items())

    def keys(self) -> Any:
        with self._lock:
            return list(super().keys())

    def pop(self, key: K, default: Any = ...) -> Any:
        with self._lock:
            if default is ...:
                return super().pop(key)
            return super().pop(key, default)

    def popitem(self) -> tuple[K, V]:
        with self._lock:
            return super().popitem()

    def setdefault(self, key: K, default: Any = None) -> V:
        with self._lock:
            return super().setdefault(key, default)

    def update(self, *args: Any, **kwargs: Any) -> None:
        with self._lock:
            super().update(*args, **kwargs)

    def values(self) -> Any:
        with self._lock:
            return list(super().values())

    def __enter__(self) -> LockableDict[K, V]:
        """コンテキストマネージャを開始し、ロックを取得する。"""
        self._lock.acquire()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """コンテキストマネージャを終了し、ロックを解放する。"""
        self._lock.release()

    def __reduce__(self) -> tuple[Any, ...]:
        """pickle化およびcopy時の再構築手順を定義する。"""
        with self._lock:
            state = self.__dict__.copy()
            state.pop("_lock", None)
            return (self.__class__, (dict(self),), state)


class LockableList[V](list[V]):
    """要素の操作時にthreading.RLockを使用するスレッドセーフなlistクラス。

    個々のメソッド（append, extend, pop等）は自動的にロックで保護されます。
    また、with構文を使用することで、複数の操作をアトミックに実行できます。
    RLockを使用しているため、同一スレッド内での再入（二重ロック）が可能です。
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """LockableListを初期化する。"""
        super().__init__(*args, **kwargs)
        self._lock = RLock()

    def __contains__(self, key: object) -> bool:
        with self._lock:
            return super().__contains__(key)

    def __delitem__(
        self,
        key: SupportsIndex | slice[SupportsIndex | None, SupportsIndex | None, SupportsIndex | None],
    ) -> None:
        with self._lock:
            super().__delitem__(key)

    @overload
    def __getitem__(self, i: SupportsIndex, /) -> V: ...

    @overload
    def __getitem__(
        self,
        s: slice[SupportsIndex | None, SupportsIndex | None, SupportsIndex | None],
        /,
    ) -> LockableList[V]: ...

    def __getitem__(
        self,
        item: SupportsIndex | slice[SupportsIndex | None, SupportsIndex | None, SupportsIndex | None],
        /,
    ) -> Any:
        with self._lock:
            res = super().__getitem__(item)
            return LockableList[V](res) if isinstance(item, slice) else res

    def __iter__(self) -> Iterator[V]:
        with self._lock:
            return iter(list(super().__iter__()))

    def __len__(self) -> int:
        with self._lock:
            return super().__len__()

    @overload
    def __setitem__(self, key: SupportsIndex, value: V) -> None: ...

    @overload
    def __setitem__(
        self,
        key: slice[SupportsIndex | None, SupportsIndex | None, SupportsIndex | None],
        value: Iterable[V],
    ) -> None: ...

    def __setitem__(
        self,
        key: SupportsIndex | slice[SupportsIndex | None, SupportsIndex | None, SupportsIndex | None],
        value: V | Iterable[V],
    ) -> None:
        with self._lock:
            super().__setitem__(key, value)  # type: ignore[arg-type]

    def __iadd__(self, other: Iterable[V]) -> LockableList[V]:
        with self._lock:
            super().__iadd__(other)
            return self

    def __imul__(self, value: SupportsIndex) -> LockableList[V]:
        with self._lock:
            super().__imul__(value)
            return self

    def append(self, obj: V, /) -> None:
        with self._lock:
            super().append(obj)

    def clear(self) -> None:
        with self._lock:
            super().clear()

    def copy(self) -> LockableList[V]:
        with self._lock:
            return LockableList(super().copy())

    def count(self, value: Any, /) -> int:
        with self._lock:
            return super().count(value)

    def extend(self, iterable: Iterable[V], /) -> None:
        with self._lock:
            super().extend(iterable)

    def index(
        self,
        value: Any,
        start: SupportsIndex = 0,
        stop: SupportsIndex | None = None,
        /,
    ) -> int:
        with self._lock:
            if stop is None:
                return super().index(value, start)
            return super().index(value, start, stop)

    def insert(self, index: SupportsIndex, obj: V, /) -> None:
        with self._lock:
            super().insert(index, obj)

    def pop(self, index: SupportsIndex = -1, /) -> V:
        with self._lock:
            return super().pop(index)

    def remove(self, value: Any, /) -> None:
        with self._lock:
            super().remove(value)

    def reverse(self) -> None:
        with self._lock:
            super().reverse()

    def sort(self, *, key: Any = None, reverse: bool = False) -> None:
        with self._lock:
            super().sort(key=key, reverse=reverse)

    def __enter__(self) -> LockableList[V]:
        self._lock.acquire()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self._lock.release()

    def __reduce__(self) -> tuple[Any, ...]:
        with self._lock:
            state = self.__dict__.copy()
            state.pop("_lock", None)
            return (self.__class__, (list(self),), state)


class ObjectStore[T = Any]:
    """オブジェクトを pickle 化してファイルに保存・管理するクラス。

    特殊な変換が必要なクラスを保存する場合は、対象のクラスで `__reduce__`
    メソッドを実装することで、リスト内の要素などを含め自動的にカスタム
    シリアライズが適用される。

    Attributes:
        _file (Path): 保存先のファイルパス。
        _obj (T | None): 現在メモリ上に保持されているオブジェクト。
        _validator (Callable[[object], bool] | None): データ検証用関数。
        _allow_validation_failure (bool): 検証失敗時に None を許容するかどうか。
    """

    def __init__(
        self,
        file: StrPath,
        validator: Callable[[object], TypeGuard[T]] | None = None,
        allow_validation_failure: bool = False,
    ) -> None:
        """ObjectStoreを初期化する。

        Args:
            file (StrPath): 保存先ファイルパス。
            validator (Callable[[object], TypeGuard[T]] | None, optional): オブジェクトの検証関数。 Defaults to None.
            allow_validation_failure (bool, optional): validatorがインスタンス生成時に失敗した場合、`self.obj=None`として初期化することを許容するか。

        Raises:
            PathTypeError: 指定されたパスがディレクトリとして存在する場合。
            TypeError: 自動読み込み時の検証に失敗し、allow_validation_failure が False の場合。
            ObjectStoreLoadError: ファイル読み込みまたは復元に失敗した場合。
        """
        self._file = file = setup_path(file)

        if file.is_dir():
            msg = f"`{file}`はディレクトリとして存在しています。"
            raise PathTypeError(msg)

        self._validator = validator
        try:
            self._obj: T | None = self.load_file()
        except TypeError:
            if not allow_validation_failure:
                raise
            self._obj = None

    @staticmethod
    def dumps(obj: object) -> str:
        """オブジェクトを`base64`エンコードされた`pickle`文字列に変換する。

        Args:
            obj (object): 変換対象オブジェクト。

        Returns:
            str: `base64`エンコードされた文字列。
        """
        data = pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
        return base64.b64encode(data).decode("utf-8")

    @staticmethod
    def loads(pickle_str: str) -> Any:
        """`base64`文字列をオブジェクトに復元する。

        Args:
            pickle_str (str): 復元対象の`base64`文字列。

        Returns:
            Any: 復元されたオブジェクト。文字列が空の場合は`None`。
        """
        if not pickle_str:
            return None
        data = base64.b64decode(pickle_str.encode())
        return pickle.loads(data)

    def load_file(self) -> T | None:
        """ファイルからオブジェクトを読み込む。

        インスタンス実行時にも自動的に実行される。

        Raises:
            TypeError: 検証関数による検証に失敗した場合。
            ObjectStoreLoadError: ファイルの読み込みやBase64 / pickleデコードに失敗した場合。

        Returns:
            T | None: 読み込んだオブジェクト。
        """
        if not self._file.exists():
            return None

        try:
            with self._file.open("r", encoding="utf-8") as f:
                content = f.read()
            raw_obj = self.loads(content)
        except Exception as ex:
            msg = f"`{self._file}`からのデータ読み込み・復元に失敗しました。"
            raise ObjectStoreLoadError(msg) from ex

        if raw_obj is not None and (validator := self._validator) is not None and not validator(raw_obj):
            msg = f"`{self._file}`のデータは検証関数を通過しませんでした（type: {type(raw_obj)}）。"
            raise TypeError(msg)

        return raw_obj

    def save_file(self, obj: T | None) -> bool:
        """オブジェクトをシリアライズしてファイルに保存する。

        Args:
            obj (T | None): 保存するオブジェクト。

        Returns:
            bool: 保存に成功した場合は`True`、失敗した場合は`False`。
        """
        if obj is not None and (validator := self._validator) is not None and not validator(obj):
            return False
        try:
            content = self.dumps(obj)

            tmp_fd, tmp_path_str = tempfile.mkstemp(dir=self._file.parent, prefix=".tmp")
            pf_tmp = Path(tmp_path_str)

            try:
                with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                    f.write(content)
                    f.flush()
                    os.fsync(f.fileno())
                pf_tmp.replace(self._file)
                self._obj = obj
                return True
            except Exception:
                if pf_tmp.exists():
                    pf_tmp.unlink()
                return False
        except Exception:
            return False

    @property
    def obj(self) -> T | None:
        """保存されているオブジェクト。"""
        return self._obj


class Timer:
    """指定時間の経過判定および待機を行うタイマー。

    同期的な待機 (`join`) と非同期的な待機 (`ajoin`) の両方をサポートする。
    また、残り時間を逐次取得するイテレータ機能 (`wiggle_join`, `awiggle_join`) も備えています。
    """

    def __init__(
        self,
        hours: int = 0,
        minutes: int = 0,
        seconds: float = 0,
    ) -> None:
        """Timer を初期化する。

        Args:
            hours (int): 時間。 Defaults to 0.
            minutes (int): 分。 Defaults to 0.
            seconds (float): 秒。 Defaults to 0.

        Raises:
            ValueError: 指定された時間が 0 秒未満の場合。
        """
        delta = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        if delta < timedelta(0):
            msg = f"0秒未満のタイマーは作成できません: {delta.total_seconds()}s"
            raise ValueError(msg)
        self._delta = delta
        self.reset()

    def __bool__(self) -> bool:
        """タイマーが稼働中（終了時刻に達していない）かどうかを取得する。"""
        return self.is_active

    def __repr__(self) -> str:
        return f"Timer(delta={self.delta.total_seconds()}s, target={self.target_time})"

    def __str__(self) -> str:
        h, m, s = self.calc_hms(self.delta.total_seconds())
        parts = []
        if h > 0:
            parts.append(f"{h}時間")
        if m > 0:
            parts.append(f"{m}分")
        if s > 0:
            parts.append(f"{s}秒")
        return "".join(parts) + "のタイマー"

    @staticmethod
    def calc_hms(seconds: float) -> HMSTuple:
        """秒数を (時, 分, 秒) の形式に変換する。

        Args:
            seconds (float): 変換する秒数。

        Returns:
            HMSTuple: (時, 分, 秒) のタプル。
        """
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return (int(h), int(m), s)

    def begin(self, span_seconds: float = 0) -> None:
        """タイマーをリセットし、同期的に待機を開始する。

        Args:
            span_seconds (float): 終了判定の間隔（秒）。 Defaults to 0.
        """
        self.reset()
        self.join(span_seconds)

    async def abegin(self, span_seconds: float = 0) -> None:
        """タイマーをリセットし、非同期的に待機を開始する。

        Args:
            span_seconds (float): 終了判定の間隔（秒）。 Defaults to 0.
        """
        self.reset()
        await self.ajoin(span_seconds)

    def join(self, span_seconds: float = 0) -> None:
        """終了時刻まで現在のスレッドをブロックして待機する。

        Args:
            span_seconds (float): 終了判定を行う間隔（秒）。 Defaults to 0.
        """
        if span_seconds <= 0:
            rem = self.remaining_seconds
            if rem > 0:
                time.sleep(rem)
            return

        span_seconds = max(span_seconds, 0.001)
        while self.is_active:
            rem = self.remaining_seconds
            if rem <= 0:
                break
            time.sleep(min(span_seconds, rem))

    async def ajoin(self, span_seconds: float = 0) -> None:
        """終了時刻までイベントループをブロックせずに非同期待機する。

        Args:
            span_seconds (float): 終了判定を行う間隔（秒）。 Defaults to 0.
        """
        if span_seconds <= 0:
            rem = self.remaining_seconds
            if rem > 0:
                await asyncio.sleep(rem)
            return

        span_seconds = max(span_seconds, 0.001)
        while self.is_active:
            rem = self.remaining_seconds
            if rem <= 0:
                break
            await asyncio.sleep(min(span_seconds, rem))

    def reset(self) -> None:
        """開始時刻を現在時刻に更新し、タイマーをリセットする。"""
        self._start_time = datetime.now()
        self._start_monotonic = time.monotonic()
        self._target_time = self._start_time + self._delta

    def wiggle_begin(self, interval_seconds: float = 0.1) -> Iterator[HMSTuple]:
        """タイマーをリセットし、残り時間をyieldする同期イテレータを開始する。

        Args:
            interval_seconds (float, optional): 更新及び待機インターバル（秒）。 Defaults to 0.1.

        Yields:
            Iterator[HMSTuple]: (時, 分, 秒) のタプル。
        """
        self.reset()
        yield from self.wiggle_join(interval_seconds=interval_seconds)

    def wiggle_join(self, interval_seconds: float = 0.1) -> Iterator[HMSTuple]:
        """終了時刻まで残り時刻をyieldし続ける同期イテレータ。

        Args:
            interval_seconds (float, optional): 更新及び待機インターバル（秒）。 Defaults to 0.1.

        Yields:
            Iterator[HMSTuple]: (時, 分, 秒) のタプル。
        """
        interval_seconds = max(interval_seconds, 0.001)

        while self.is_active:
            rem = self.remaining_seconds
            yield self.calc_hms(rem)
            if rem <= 0:
                break
            time.sleep(min(interval_seconds, rem))

    def awiggle_begin(self, interval_seconds: float = 0.1) -> AsyncIterator[HMSTuple]:
        """タイマーをリセットし、残り時間をyieldする非同期イテレータを開始する。

        Args:
            interval_seconds (float, optional): 更新及び待機インターバル（秒）。 Defaults to 0.1.

        Yields:
            AsyncIterator[HMSTuple]: (時, 分, 秒) のタプル。
        """
        self.reset()
        return self.awiggle_join(interval_seconds=interval_seconds)

    async def awiggle_join(self, interval_seconds: float = 0.1) -> AsyncIterator[HMSTuple]:
        """終了時刻まで残り時間をyieldし続ける非同期イテレータ。

        Args:
            interval_seconds (float, optional): 更新及び待機インターバル（秒）。 Defaults to 0.1.

        Yields:
            AsyncIterator[HMSTuple]: (時, 分, 秒) のタプル。
        """
        interval_seconds = max(interval_seconds, 0.001)

        while self.is_active:
            rem = self.remaining_seconds
            yield self.calc_hms(rem)
            if rem <= 0:
                break
            await asyncio.sleep(min(interval_seconds, rem))

    @property
    def delta(self) -> timedelta:
        """設定された時間隔を取得する。"""
        return self._delta

    @property
    def is_active(self) -> bool:
        """タイマーが稼働中（終了時刻に達していない）かどうかを取得する。"""
        return self.remaining_seconds > 0

    @property
    def remaining_seconds(self) -> float:
        """残り時間を秒数（float）で取得する。"""
        elapsed = time.monotonic() - self._start_monotonic
        return max(0.0, self._delta.total_seconds() - elapsed)

    @property
    def remaining_time(self) -> timedelta:
        return timedelta(seconds=self.remaining_seconds)

    @property
    def start_time(self) -> datetime:
        """タイマーの開始時刻を取得する。"""
        return self._start_time

    @property
    def target_time(self) -> datetime:
        """タイマーの終了目標時刻を取得する。"""
        return self._target_time
