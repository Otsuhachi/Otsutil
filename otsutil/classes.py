import base64
import pickle
import time

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, ClassVar, Generator, TypeVar, Union

from .funcs import setup_path

FLOAT_INT = TypeVar('FLOAT_INT', float, int)


class ObjectSaver:
    """オブジェクトを保存するファイルを扱うクラスです。
    """
    def __init__(self, file: Union[str, Path]):
        """オブジェクトを保存するファイルを準備します。

        Args:
            file (Union[str, Path]): オブジェクトを保存するファイルです。
        """
        self.__file = setup_path(file)

    @staticmethod
    def dumps(obj: Any) -> str:
        """オブジェクトのpickle文字列を取得します。

        Args:
            obj (Any): pickle文字列を取得したいオブジェクトです。

        Returns:
            str: pickle文字列です。
        """
        otb = pickle.dumps(obj, protocol=4)
        return base64.b64encode(otb).decode('utf-8')

    @staticmethod
    def loads(pickle_str: str) -> Any:
        """pickle文字列をオブジェクト化します。

        Args:
            pickle_str (str): pickle文字列です。

        Returns:
            Any: 復元されたオブジェクトです。
        """
        stb = base64.b64decode(pickle_str.encode())
        return pickle.loads(stb)

    def load_file(self) -> Any:
        """ファイルに保存されているデータを読み込み、取得します。

        ファイルが存在しなかった場合にはNoneを保存したファイルを生成し、Noneを返します。

        Returns:
            Any: ファイルに保存されていたオブジェクトです。
        """
        if self.__file.exists():
            with open(self.__file, 'r', encoding='utf-8') as f:
                return self.loads(f.read())
        else:
            self.save_file(None)
        return None

    def save_file(self, obj: Any) -> bool:
        """ファイルにobjを保存します。

        また、loadメソッドで取得できるオブジェクトを更新します。

        Args:
            obj (Any): 保存したいオブジェクトです。

        Returns:
            bool: 保存の成否です。
        """
        try:
            bts = self.dumps(obj)
            with open(self.__file, 'w', encoding='utf-8') as f:
                f.write(bts)
            return True
        except Exception as e:
            return False


class OtsuNoneType:
    """Noneが返るのが正常な場合など、異常なNoneを表す場合に使用するクラスです。
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return 'OtsuNone'

    def __bool__(self) -> bool:
        return False


class Timer:
    """指定時間が経過したかを判定したり指定時間秒処理を停止させるタイマーのクラスです。
    """
    HOUR_SECONDS: ClassVar[int] = 3600
    MINUTE_SECONDS: ClassVar[int] = 60
    MINIMUM_SECONDS: ClassVar[float] = 0.005

    @classmethod
    def check_minimum_seconds(cls, seconds: FLOAT_INT) -> FLOAT_INT:
        """指定秒数がTimerクラスで使用可能かを判定し、使用不能な場合には例外を発生させます。

        Args:
            seconds (FLOAT_INT): 指定秒数。

        Raises:
            ValueError: Timerクラスで使用不可能な指定秒数が与えられた場合に投げられます。

        Returns:
            FLOAT_INT: seconds.
        """
        if cls.MINIMUM_SECONDS > seconds:
            msg = f'{cls.MINIMUM_SECONDS}秒未満の秒数を指定することはできません。'
            raise ValueError(msg)
        return seconds

    def __init__(self, hours: int = 0, minutes: int = 0, seconds: int = 0) -> None:
        """h時間m分s秒を測るタイマーインスタンスを生成します。

        Args:
            hours (int, optional): h時間。
            minutes (int, optional): m分。
            seconds (int, optional): s秒。
        """
        seconds += hours * Timer.HOUR_SECONDS
        seconds += minutes * Timer.MINUTE_SECONDS
        seconds = Timer.check_minimum_seconds(seconds)
        self.__seconds = timedelta(seconds=seconds)
        self.reset()

    def begin(self, span_seconds: float = 0) -> None:
        """現在から指定時間秒待機します。

        Args:
            span_seconds (float, optional): 待機終了を確認する頻度。
        """
        self.reset()
        self.join(span_seconds)

    def join(self, span_seconds: float = 0) -> None:
        """開始時刻から指定時間秒経過するまで待機します。

        Timer.beginと違い、インスタンス生成やTimer.resetからの経過時間に応じて待機時間が減少します。

        Args:
            span_seconds (float, optional): 待機終了を確認する頻度。
        """
        span = Timer.check_minimum_seconds(span_seconds)
        while self:
            time.sleep(span)

    def reset(self) -> None:
        """タイマーの開始時刻をリセットし、終了時刻を更新します。
        """
        self.__start_time = datetime.now()
        self.__target_time = self.__start_time + self.__seconds

    def wiggle_begin(self, span_seconds: float = 0) -> Generator[None, None, None]:
        """for文で使用することで処理を割り込ませられるTimer.beginです。

        Args:
            span_seconds (float, optional): 処理割込み可能にする頻度秒。

        Yields:
            Generator[None, None, None]: None.
        """
        self.reset()
        yield from self.wiggle_join(span_seconds)

    def wiggle_join(self, span_seconds: float = 0) -> Generator[None, None, None]:
        """for文で使用することで処理を割り込ませられるTimer.joinです。

        Args:
            span_seconds (float, optional): 処理割込み可能にする頻度秒。

        Yields:
            Generator[None, None, None]: None.
        """
        span = Timer.check_minimum_seconds(span_seconds)
        while self:
            yield
            time.sleep(span)

    @property
    def seconds(self) -> timedelta:
        """このタイマーの秒数です。
        """
        return self.__seconds

    @property
    def start_time(self) -> datetime:
        """タイマーを開始した時刻です。

        この時刻を基準にseconds秒経過したかを判定します。
        インスタンス生成時、またはTimer.begin, Timer.resetメソッドを呼び出した場合にこの属性が変更されます。
        """
        return self.__start_time

    @property
    def target_time(self) -> datetime:
        """タイマーを終了する時刻です。

        インスタンス生成時、またはTimer.begin, Timer.resetメソッドを呼び出した場合にこの属性が変更されます。
        """
        return self.__target_time

    def __str__(self) -> str:
        seconds = self.__seconds.total_seconds()
        h, seconds = divmod(seconds, Timer.HOUR_SECONDS)
        m, seconds = divmod(seconds, Timer.MINUTE_SECONDS)
        res = []
        for i, s in zip(map(int, (h, m, seconds)), ('時間', '分', '秒')):
            if i > 0:
                res.append(f'{i}{s}')
        return ''.join(res) + 'のタイマーです。'

    def __bool__(self) -> bool:
        return self.__target_time > datetime.now()


OtsuNone = OtsuNoneType()
