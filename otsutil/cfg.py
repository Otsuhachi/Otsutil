"""よく使う定数を纏めたモジュール。"""

__all__ = ["JST"]


from datetime import timedelta, timezone

JST = timezone(timedelta(hours=9), "JST")
