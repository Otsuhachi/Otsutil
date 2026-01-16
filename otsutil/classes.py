"""よく使うクラスを纏めたモジュールです。"""

__all__ = (
    "LockableDict",
    "LockableList",
    "ObjectSaver",
    "OtsuNone",
    "Timer",
)


import base64
import pickle
import time
from collections.abc import Callable, Iterator
from datetime import datetime, timedelta
from threading import Lock
from typing import Any

from .funcs import setup_path
from .types import hmsValue, pathLike


class __OtsuNoneType:
    """異常な None を表すためのセンチネルクラス。"""

    def __repr__(self) -> str:
        return "OtsuNone"

    def __bool__(self) -> bool:
        return False


OtsuNone: Any = __OtsuNoneType()


class LockableDict[K, V](dict[K, V]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._lock = Lock()

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
        with self._lock:
            super().__delitem__(key)

    def __getitem__(self, key: K) -> V:
        with self._lock:
            return super().__getitem__(key)

    def __setitem__(self, key: K, value: V) -> None:
        with self._lock:
            return super().__setitem__(key, value)

    def _with_lock[**P, R](self, f: Callable[P, R]) -> Callable[P, R]:
        """メソッドをロックでラップします。"""

        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with self._lock:
                return f(*args, **kwargs)

        return wrapper


class LockableList[V](list[V]):
    """要素の操作時に threading.Lock を使用する list クラス。"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._lock = Lock()
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

    def _with_lock[**P, R](self, f: Callable[P, R]) -> Callable[P, R]:
        """メソッドをロックでラップします。"""

        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with self._lock:
                return f(*args, **kwargs)

        return wrapper


class ObjectSaver[T]:
    """オブジェクトを pickle 化してファイルに保存するクラス。

    特殊な変換が必要なクラスを保存する場合は、対象のクラスで `__reduce__`
    メソッドを実装することで、リスト内の要素などを含め自動的にカスタム
    シリアライズが適用されます。

    Attributes:
        obj (T | None): 保存されているオブジェクト。
    """

    def __init__(self, file: pathLike) -> None:
        """ObjectSaver を初期化します。

        Args:
            file (pathLike): 保存先のファイルパス。
        """
        self._file = setup_path(file)
        self._obj: T | None = self.load_file() if self._file.exists() else None

    @staticmethod
    def dumps(obj: Any) -> str:  # noqa: ANN401
        """オブジェクトを base64 エンコードされた pickle 文字列に変換します。

        Args:
            obj (Any): 変換対象のオブジェクト。

        Returns:
            str: base64 文字列。
        """
        data = pickle.dumps(obj, protocol=4)
        return base64.b64encode(data).decode("utf-8")

    @staticmethod
    def loads(pickle_str: str) -> Any:  # noqa: ANN401
        """base64 文字列をオブジェクトに復元します。

        Args:
            pickle_str (str): base64 文字列。

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
            T | None: 読み込まれたオブジェクト。ファイルがない場合は None。
        """
        if self._file.exists():
            with self._file.open("r", encoding="utf-8") as f:
                return self.loads(f.read())
        self.save_file(None)
        return None

    def save_file(self, obj: T | None) -> bool:
        """オブジェクトをファイルに保存します。

        Args:
            obj (T | None): 保存するオブジェクト。

        Returns:
            bool: 保存に成功した場合は True。
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
        """現在保持されているオブジェクト。"""
        return self._obj


class Timer:
    """指定時間の経過判定および待機を行うタイマー。"""

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
            msg = f"０秒未満のタイマーは作成できません: {delta.total_seconds()}s"
            raise ValueError(msg)
        self._delta = delta
        self.reset()

    def __bool__(self) -> bool:
        """タイマーが稼働中（終了時刻に達していない）か。"""
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
    def calc_hms(seconds: float) -> hmsValue:
        """秒数を (時, 分, 秒) に変換します。"""
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return (int(h), int(m), s)

    def begin(self, span_seconds: float = 0) -> None:
        """タイマーをリセットして待機を開始します。"""
        self.reset()
        self.join(span_seconds)

    def join(self, span_seconds: float = 0) -> None:
        """終了時刻までスレッドをブロックします。

        Args:
            span_seconds (float): 終了判定を行う間隔（秒）。 Defaults to 0.
        """
        span = max(0.0, span_seconds)
        while self:
            time.sleep(span)

    def reset(self) -> None:
        """開始時刻を現在に更新します。"""
        self._start_time = datetime.now()
        self._target_time = self._start_time + self._delta

    def wiggle_begin(self) -> Iterator[hmsValue]:
        """リセットして残り時間を yield するイテレータ。"""
        self.reset()
        yield from self.wiggle_join()

    def wiggle_join(self) -> Iterator[hmsValue]:
        """終了まで残り時間を yield し続けるイテレータ。

        Yields:
            Iterator[hmsValue]: (時, 分, 秒) のタプル。
        """
        while self:
            diff = self.target_time - datetime.now()
            yield self.calc_hms(max(0, diff.total_seconds()))

    @property
    def delta(self) -> timedelta:
        return self._delta

    @property
    def start_time(self) -> datetime:
        return self._start_time

    @property
    def target_time(self) -> datetime:
        return self._target_time
