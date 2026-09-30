from datetime import timedelta, timezone

"""よく使う定数を纏めたモジュール。"""

__all__ = ["JST"]


JST = timezone(timedelta(hours=9), "JST")
