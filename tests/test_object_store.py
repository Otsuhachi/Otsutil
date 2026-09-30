import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TypeGuard

sys.path.append(str(Path.cwd()))

from otsutil.classes import ObjectStore
from otsutil.exceptions import ObjectStoreLoadError, PathTypeError
from otsutil.funcs import is_dict_type


def is_int_dict(obj: object) -> TypeGuard[dict[str, int]]:
    return isinstance(obj, dict) and is_dict_type(obj, str, int)


class TestObjectStore(unittest.TestCase):
    """ObjectStore の機能を検証するテストクラス。"""

    def test_save_and_load_file(self) -> None:
        """正常な保存と読み込みの基本操作テスト。"""
        with TemporaryDirectory() as pd_tmp:
            pf = Path(pd_tmp) / "data.txt"
            store = ObjectStore[dict[str, int]](pf)

            data = {"a": 100, "b": 200}
            self.assertTrue(store.save_file(data))
            self.assertEqual(store.obj, data)

            # 新規インスタンス作成時の自動ロード確認
            store_loaded = ObjectStore(pf)
            self.assertEqual(store_loaded.obj, data)

    def test_validator_success_and_failure(self) -> None:
        """validator による型検証の挙動テスト。"""
        with TemporaryDirectory() as pd_tmp:
            pf = Path(pd_tmp) / "validated.txt"
            store = ObjectStore(pf, validator=is_int_dict)

            # 不正なデータはsave_fileがFalseを返す
            invalid_data = {"a": "not_an_int"}
            self.assertFalse(store.save_file(invalid_data))  # type: ignore

            # 正しいデータ保存
            valid_data = {"a": 1}
            self.assertTrue(store.save_file(valid_data))

            # 正常にロードできること
            store_loaded = ObjectStore(pf, validator=is_int_dict)
            self.assertEqual(store_loaded.obj, valid_data)

    def test_allow_validation_failure(self) -> None:
        """allow_validation_failure の切り替え動作テスト。"""
        with TemporaryDirectory() as pd_tmp:
            pf = Path(pd_tmp) / "data.txt"

            # 検証無しで不正データを直接書き込み
            raw_store = ObjectStore(pf)
            raw_store.save_file("StringData")

            # allow_validation_failure=Falseの場合はTypeErrorが送出される
            with self.assertRaises(TypeError):
                ObjectStore(pf, validator=is_int_dict, allow_validation_failure=False)

            # allow_validation_failure=Trueの場合はself.objがNoneになる
            store_allowed = ObjectStore(pf, validator=is_int_dict, allow_validation_failure=True)
            self.assertIsNone(store_allowed.obj)

    def test_directory_path_raises_path_type_error(self) -> None:
        """ディレクトリパス指定時に PathTypeError が発生することのテスト。"""
        with TemporaryDirectory() as pd_tmp:
            pd = Path(pd_tmp)
            with self.assertRaises(PathTypeError):
                ObjectStore(pd)

    def test_atomic_save_and_auto_created_dir(self) -> None:
        """初期化時の親ディレクトリ生成およびアトミック保存のテスト。"""
        with TemporaryDirectory() as pd_tmp:
            pf = Path(pd_tmp) / "nested" / "sub" / "data.txt"
            store = ObjectStore(pf)

            # インスタンス生成時点で親フォルダが存在していること
            self.assertTrue(pf.parent.exists())

            self.assertTrue(store.save_file("Hello"))
            self.assertTrue(pf.exists())

            # 不正なシリアライズデータ等でエラーになっても元ファイルが保持されるか
            unpicklable = lambda: None  # noqa: E731
            self.assertFalse(store.save_file(unpicklable))
            self.assertEqual(store.load_file(), "Hello")

    def test_corrupted_file_raises_load_error(self) -> None:
        """破損ファイル読み込み時に ObjectStoreLoadError が送出されることのテスト。"""
        with TemporaryDirectory() as pd_tmp:
            pf = Path(pd_tmp) / "corrupted.txt"
            pf.write_text("invalid_base_64_content!!!", encoding="utf-8")

            with self.assertRaises(ObjectStoreLoadError):
                ObjectStore(pf)


if __name__ == "__main__":
    unittest.main()
