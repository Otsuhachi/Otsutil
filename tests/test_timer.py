import asyncio
import sys
import time
import unittest
from pathlib import Path

sys.path.append(str(Path.cwd()))

from otsutil.classes import Timer


class TestTimer(unittest.TestCase):
    """Timer の機能を検証するテストクラス。"""

    def test_basic_timer_properties(self) -> None:
        """タイマーの基本プロパティおよび初期化の検証。"""
        timer = Timer(seconds=0.2)
        self.assertTrue(timer.is_active)
        self.assertTrue(bool(timer))
        self.assertGreater(timer.remaining_seconds, 0)
        self.assertIn("のタイマー", str(timer))

        time.sleep(0.25)
        self.assertFalse(timer.is_active)
        self.assertFalse(bool(timer))
        self.assertEqual(timer.remaining_seconds, 0.0)

    def test_invalid_timer(self) -> None:
        """0秒未満のタイマーでValueErrorが発生することを検証。"""
        with self.assertRaises(ValueError):
            Timer(seconds=-1)

    def test_join(self) -> None:
        """同期ブロック待機（join）の検証。"""
        timer = Timer(seconds=0.1)
        start = time.monotonic()
        timer.join(span_seconds=0.02)
        elapsed = time.monotonic() - start

        self.assertGreaterEqual(elapsed, 0.09)
        self.assertFalse(timer.is_active)

    def test_async_join(self) -> None:
        """非同期待機（ajoin）の検証。"""

        async def run_test() -> None:
            timer = Timer(seconds=0.1)
            start = time.monotonic()
            await timer.ajoin(span_seconds=0.02)
            elapsed = time.monotonic() - start

            self.assertGreaterEqual(elapsed, 0.09)
            self.assertFalse(timer.is_active)

        asyncio.run(run_test())

    def test_wiggle_join(self) -> None:
        """wiggle_joinイテレータの検証。"""
        timer = Timer(seconds=0.15)
        hms_list = list(timer.wiggle_join(interval_seconds=0.05))

        self.assertGreater(len(hms_list), 0)
        self.assertFalse(timer.is_active)

    def test_async_wiggle_join(self) -> None:
        """awiggle_joinイテレータの動作検証。"""

        async def run_test() -> None:
            timer = Timer(seconds=0.15)
            results = [hms async for hms in timer.awiggle_join(interval_seconds=0.05)]
            self.assertGreater(len(results), 0)
            self.assertFalse(timer.is_active)

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
