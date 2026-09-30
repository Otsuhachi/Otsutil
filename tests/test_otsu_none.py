import copy
import pickle
import sys
import unittest
from pathlib import Path

sys.path.append(str(Path.cwd()))

from otsutil.classes import OtsuNone, OtsuNoneType


class TestOtsuNone(unittest.TestCase):
    """OtsuNone センチネルオブジェクトの検証テストクラス。"""

    def test_behavior(self) -> None:
        """bool 判定、repr、型クラスの検証。"""
        self.assertFalse(bool(OtsuNone))
        self.assertEqual(repr(OtsuNone), "OtsuNone")
        self.assertIsInstance(OtsuNone, OtsuNoneType)

    def test_singleton_copy_and_pickle(self) -> None:
        """copy / deepcopy / pickle 後も同一性が維持されるか検証。"""
        copied = copy.copy(OtsuNone)
        deep_copied = copy.deepcopy(OtsuNone)
        self.assertIs(copied, OtsuNone)
        self.assertIs(deep_copied, OtsuNone)

        dumped = pickle.dumps(OtsuNone)
        restored = pickle.loads(dumped)
        self.assertIs(restored, OtsuNone)


if __name__ == "__main__":
    unittest.main()
