"""よく使うクラスを纏めたモジュールです。"""

__all__ = (
    "LockableDict",
    "LockableList",
    "ObjectStore",
    "OtsuNone",
    "Timer",
)


import asyncio
import base64
import pickle
import time
from collections.abc import AsyncIterator, Callable, Iterator
from datetime import datetime, timedelta
from threading import RLock
from typing import Any

from .funcs import setup_path
from .types import HMSTuple, StrPath


class __OtsuNoneType:
    """異常な None を表すためのセンチネルクラス。"""

    def __repr__(self) -> str:
        return "OtsuNone"

    def __bool__(self) -> bool:
        return False


OtsuNone: Any = __OtsuNoneType()


class LockableDict[K, V](dict[K, V]):
    """要素の操作時に threading.RLock を使用するスレッドセーフな dict クラス。

    個々のメソッド（get, pop, update等）は自動的にロックで保護されます。
    また、`with obj:` 構文を使用することで、複数の操作をアトミックに実行できます。
    RLock を使用しているため、同一スレッド内での再入（二重ロック）が可能です。
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """LockableDict を初期化します。"""
        super().__init__(*args, **kwargs)
        self._lock = RLock()

        # 動的にロックを適用するメソッド群
        attrs = (
            "clear",
            "copy",
            "fromkeys",
            "get",
            "items",
            "keys",
            "pop",
            "popitem",
            "setdefault",
            "update",
            "values",
        )
        for attr in attrs:
            if (original_method := getattr(self, attr, None)) is not None:
                setattr(self, attr, self._with_lock(original_method))

    def __delitem__(self, key: K) -> None:
        """指定したキーの要素を削除します（スレッドセーフ）。"""
        with self._lock:
            super().__delitem__(key)

    def __getitem__(self, key: K) -> V:
        """指定したキーの要素を取得します（スレッドセーフ）。"""
        with self._lock:
            return super().__getitem__(key)

    def __setitem__(self, key: K, value: V) -> None:
        """指定したキーに値を設定します（スレッドセーフ）。"""
        with self._lock:
            return super().__setitem__(key, value)

    def __enter__(self) -> "LockableDict[K, V]":
        """コンテキストマネージャを開始し、ロックを取得します。"""
        self._lock.acquire()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """コンテキストマネージャを終了し、ロックを解放します。"""
        self._lock.release()

    def _with_lock[**P, R](self, f: Callable[P, R]) -> Callable[P, R]:
        """メソッドをロックでラップします。"""

        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with self._lock:
                return f(*args, **kwargs)

        return wrapper


class LockableList[V](list[V]):
    """要素の操作時に threading.RLock を使用するスレッドセーフな list クラス。

    個々のメソッド（append, extend, pop等）は自動的にロックで保護されます。
    また、`with obj:` 構文を使用することで、複数の操作をアトミックに実行できます。
    RLock を使用しているため、同一スレッド内での再入（二重ロック）が可能です。
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """LockableList を初期化します。"""
        super().__init__(*args, **kwargs)
        self._lock = RLock()
        attrs = (
            "append",
            "clear",
            "copy",
            "count",
            "extend",
            "index",
            "insert",
            "pop",
            "remove",
            "reverse",
            "sort",
        )
        for attr in attrs:
            if (original_method := getattr(self, attr, None)) is not None:
                setattr(self, attr, self._with_lock(original_method))

    def __enter__(self) -> "LockableList[V]":
        """コンテキストマネージャを開始し、ロックを取得します。"""
        self._lock.acquire()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """コンテキストマネージャを終了し、ロックを解放します。"""
        self._lock.release()

    def _with_lock[**P, R](self, f: Callable[P, R]) -> Callable[P, R]:
        """メソッドをロックでラップします。"""

        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with self._lock:
                return f(*args, **kwargs)

        return wrapper


class ObjectStore[T]:
    """オブジェクトを pickle 化してファイルに保存・管理するクラス。

    特殊な変換が必要なクラスを保存する場合は、対象のクラスで `__reduce__`
    メソッドを実装することで、リスト内の要素などを含め自動的にカスタム
    シリアライズが適用されます。

    Attributes:
        _file (Path): 保存先のファイルパス。
        _obj (T | None): 現在メモリ上に保持されているオブジェクト。
    """

    def __init__(self, file: StrPath) -> None:
        """ObjectStore を初期化します。

        Args:
            file (StrPath): 保存先のファイルパス。
        """
        self._file = setup_path(file)
        self._obj: T | None = self.load_file() if self._file.exists() else None

    @staticmethod
    def dumps(obj: Any) -> str:  # noqa: ANN401
        """オブジェクトを base64 エンコードされた pickle 文字列に変換します。

        Args:
            obj (Any): 変換対象のオブジェクト。

        Returns:
            str: base64 エンコードされた文字列。
        """
        data = pickle.dumps(obj, protocol=4)
        return base64.b64encode(data).decode("utf-8")

    @staticmethod
    def loads(pickle_str: str) -> Any:  # noqa: ANN401
        """base64 文字列をオブジェクトに復元します。

        Args:
            pickle_str (str): 復元対象の base64 文字列。

        Returns:
            Any: 復元されたオブジェクト。文字列が空の場合は None。
        """
        if not pickle_str:
            return None
        data = base64.b64decode(pickle_str.encode())
        return pickle.loads(data)

    def load_file(self) -> T | None:
        """ファイルからオブジェクトを読み込みます。

        Returns:
            T | None: 読み込まれたオブジェクト。ファイルが存在しない場合は None。
        """
        if self._file.exists():
            with self._file.open("r", encoding="utf-8") as f:
                return self.loads(f.read())
        self.save_file(None)
        return None

    def save_file(self, obj: T | None) -> bool:
        """オブジェクトをシリアライズしてファイルに保存します。

        Args:
            obj (T | None): 保存するオブジェクト。

        Returns:
            bool: 保存に成功した場合は True、失敗した場合は False。
        """
        try:
            content = self.dumps(obj)
            with self._file.open("w", encoding="utf-8") as f:
                f.write(content)
            self._obj = obj
            return True
        except Exception:
            return False

    @property
    def obj(self) -> T | None:
        """現在保持されているオブジェクトを取得します。"""
        return self._obj


class Timer:
    """指定時間の経過判定および待機を行うタイマー。

    同期的な待機 (`join`) と非同期的な待機 (`ajoin`) の両方をサポートします。
    また、残り時間を逐次取得するイテレータ機能 (`wiggle_join`, `awiggle_join`) も備えています。
    """

    def __init__(
        self,
        hours: int = 0,
        minutes: int = 0,
        seconds: float = 0,
    ) -> None:
        """Timer を初期化します。

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
        """タイマーが稼働中（終了時刻に達していない）かどうかを取得します。"""
        return self.target_time > datetime.now()

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
        """秒数を (時, 分, 秒) の形式に変換します。

        Args:
            seconds (float): 変換する秒数。

        Returns:
            HMSTuple: (時, 分, 秒) のタプル。
        """
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return (int(h), int(m), s)

    def begin(self, span_seconds: float = 0) -> None:
        """タイマーをリセットし、同期的に待機を開始します。

        Args:
            span_seconds (float): 終了判定の間隔（秒）。 Defaults to 0.
        """
        self.reset()
        self.join(span_seconds)

    async def abegin(self, span_seconds: float = 0) -> None:
        """タイマーをリセットし、非同期的に待機を開始します。

        Args:
            span_seconds (float): 終了判定の間隔（秒）。 Defaults to 0.
        """
        self.reset()
        await self.ajoin(span_seconds)

    def join(self, span_seconds: float = 0) -> None:
        """終了時刻まで現在のスレッドをブロックして待機します。

        Args:
            span_seconds (float): 終了判定を行う間隔（秒）。 Defaults to 0.
        """
        span = max(0.0, span_seconds)
        while self:
            time.sleep(span)

    async def ajoin(self, span_seconds: float = 0) -> None:
        """終了時刻までイベントループをブロックせずに非同期待機します。

        Args:
            span_seconds (float): 終了判定を行う間隔（秒）。 Defaults to 0.
        """
        span = max(0.0, span_seconds)
        while self:
            await asyncio.sleep(span)

    def reset(self) -> None:
        """開始時刻を現在時刻に更新し、タイマーをリセットします。"""
        self._start_time = datetime.now()
        self._target_time = self._start_time + self._delta

    def wiggle_begin(self) -> Iterator[HMSTuple]:
        """タイマーをリセットし、残り時間を yield する同期イテレータを開始します。

        Yields:
            Iterator[HMSTuple]: (時, 分, 秒) のタプル。
        """
        self.reset()
        yield from self.wiggle_join()

    def wiggle_join(self) -> Iterator[HMSTuple]:
        """終了時刻まで残り時間を yield し続ける同期イテレータ。

        Yields:
            Iterator[HMSTuple]: (時, 分, 秒) のタプル。
        """
        while self:
            diff = self.target_time - datetime.now()
            yield self.calc_hms(max(0, diff.total_seconds()))

    def awiggle_begin(self) -> AsyncIterator[HMSTuple]:
        """タイマーをリセットし、残り時間を yield する非同期イテレータを開始します。

        Yields:
            AsyncIterator[HMSTuple]: (時, 分, 秒) のタプル。
        """
        self.reset()
        return self.awiggle_join()

    async def awiggle_join(self) -> AsyncIterator[HMSTuple]:
        """終了時刻まで残り時間を yield し続ける非同期イテレータ。

        Yields:
            AsyncIterator[HMSTuple]: (時, 分, 秒) のタプル。
        """
        while self:
            diff = self.target_time - datetime.now()
            yield self.calc_hms(max(0, diff.total_seconds()))
            await asyncio.sleep(0)  # 他のタスクに制御を譲る

    @property
    def delta(self) -> timedelta:
        """設定された時間隔を取得します。"""
        return self._delta

    @property
    def start_time(self) -> datetime:
        """タイマーの開始時刻を取得します。"""
        return self._start_time

    @property
    def target_time(self) -> datetime:
        """タイマーの終了目標時刻を取得します。"""
        return self._target_time
