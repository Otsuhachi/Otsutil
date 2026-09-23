"""よく使う定数を纏めたモジュール。"""

__all__ = ["JST", "PD_OTSU_APP"]


from datetime import timedelta, timezone
from pathlib import Path

JST = timezone(timedelta(hours=9), "JST")
PD_OTSU_APP = Path("OtsuAppsData")
