import concurrent.futures
import copy
import pickle
import sys
import unittest
from pathlib import Path

sys.path.append(str(Path.cwd()))


from otsutil.classes import LockableDict, LockableList


class TestLockableDict(unittest.TestCase):
    """LockableDictの機能を検証するテストクラス。"""

    def test_basic_operations(self) -> None:
        d = LockableDict({"a": 1, "b": 2})

        self.assertEqual(d["a"], 1)
        self.assertIn("b", d)
        self.assertEqual(len(d), 2)

        d["c"] = 3
        self.assertEqual(d["c"], 3)

        del d["a"]
        self.assertNotIn("a", d)

        self.assertEqual(d.get("b"), 2)
        self.assertEqual(d.get("z", 99), 99)

        self.assertEqual(d.pop("b"), 2)
        self.assertNotIn("b", d)

        d.setdefault("d", 4)
        self.assertEqual(d["d"], 4)

        d.update({"e": 5})
        self.assertEqual(d["e"], 5)

        d.clear()
        self.assertEqual(len(d), 0)

    def test_in_place_or(self) -> None:
        """|=演算子による更新のテスト。"""
        d = LockableDict({"a": 1})
        d |= {"b": 2, "c": 3}
        self.assertEqual(d, {"a": 1, "b": 2, "c": 3})

    def test_views_snapshot(self) -> None:
        """keys(), values(), items(), __iter__()が独立したリスト/イテレータを返すかのテスト。"""
        d = LockableDict({"a": 1, "b": 2})

        keys = d.keys()
        values = d.values()
        items = d.items()

        self.assertIsInstance(keys, list)
        self.assertIsInstance(values, list)
        self.assertIsInstance(items, list)

        # 取得後に本体を変更してもスナップショット側には影響しないこと
        d["c"] = 3
        self.assertEqual(keys, ["a", "b"])
        self.assertEqual(values, [1, 2])
        self.assertEqual(items, [("a", 1), ("b", 2)])

        # __iter__のスナップショット確認
        iter_keys = list(iter(d))
        self.assertEqual(set(iter_keys), {"a", "b", "c"})

    def test_context_manager(self) -> None:
        """with構文による再入可能ロックのテスト。"""
        d = LockableDict({"a": 1})

        with d:
            d["b"] = 2
            with d:  # RLockの二重取得
                d["c"] = 3

        self.assertEqual(d, {"a": 1, "b": 2, "c": 3})

    def test_multithread_safety(self) -> None:
        """複数スレッドからの同時書き込み・参照時のスレッドセーフ検証。"""
        d = LockableDict[int, int]()
        num_threads = 10
        iterations = 1000

        def worker(thread_id: int) -> None:
            for i in range(iterations):
                key = (thread_id * iterations) + i
                d[key] = i
                _ = d.get(key)

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker, t) for t in range(num_threads)]
            concurrent.futures.wait(futures)

        self.assertEqual(len(d), num_threads * iterations)


class TestLockableList(unittest.TestCase):
    """LockableListの機能を検証するテストクラス。"""

    def test_basic_operations(self) -> None:
        """基本的なリスト操作のテスト。"""
        lst = LockableList([1, 2, 3])

        self.assertEqual(len(lst), 3)
        self.assertEqual(lst[0], 1)
        self.assertIn(2, lst)

        lst.append(4)
        self.assertEqual(lst, [1, 2, 3, 4])

        lst.extend([5, 6])
        self.assertEqual(lst, [1, 2, 3, 4, 5, 6])

        lst.insert(0, 0)
        self.assertEqual(lst[0], 0)

        self.assertEqual(lst.pop(), 6)
        lst.remove(0)
        self.assertNotIn(0, lst)

        lst.reverse()
        self.assertEqual(lst, [5, 4, 3, 2, 1])

        lst.sort()
        self.assertEqual(lst, [1, 2, 3, 4, 5])

    def test_slice_and_item_access(self) -> None:
        """スライス取得・代入・削除のテスト。"""
        lst = LockableList([10, 20, 30, 40, 50])

        sub = lst[1:4]
        self.assertIsInstance(sub, LockableList)
        self.assertEqual(sub, [20, 30, 40])

        lst[1:3] = [22, 33]
        self.assertEqual(lst, [10, 22, 33, 40, 50])

        del lst[0:2]
        self.assertEqual(lst, [33, 40, 50])

    def test_in_place_operators(self) -> None:
        """+=および*=演算子のテスト。"""
        lst = LockableList([1, 2])
        lst += [3, 4]
        self.assertEqual(lst, [1, 2, 3, 4])

        lst *= 2
        self.assertEqual(lst, [1, 2, 3, 4, 1, 2, 3, 4])

    def test_iter_snapshot(self) -> None:
        """__iter__()が安全なスナップショットイテレータを返すかのテスト。"""
        lst = LockableList([1, 2, 3])
        it = iter(lst)

        lst.append(4)
        self.assertEqual(list(it), [1, 2, 3])

    def test_context_manager(self) -> None:
        """with構文によるアトミック操作のテスト。"""
        lst = LockableList([10])

        with lst:
            lst.append(20)
            with lst:
                lst.append(30)

        self.assertEqual(lst, [10, 20, 30])

    def test_multithread_safety(self) -> None:
        """複数スレッドからの同時append操作での一貫性検証。"""
        lst = LockableList[int]()
        num_threads = 8
        items_per_thread = 500

        def adder() -> None:
            for i in range(items_per_thread):
                lst.append(i)

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(adder) for _ in range(num_threads)]
            concurrent.futures.wait(futures)

        self.assertEqual(len(lst), num_threads * items_per_thread)


class TestLockablePickle(unittest.TestCase):
    """Lockableオブジェクトのcopy/pickle検証テストクラス。"""

    def test_lockable_dict_pickle(self) -> None:
        """LockableDict の pickle 化確認。"""
        d = LockableDict({"a": 1})
        dumped = pickle.dumps(d)
        restored = pickle.loads(dumped)
        self.assertEqual(restored, d)

    def test_lockable_list_pickle(self) -> None:
        """LockableListのpickle化確認。"""
        lst = LockableList([1, 2, 3])
        dumped = pickle.dumps(lst)
        restored = pickle.loads(dumped)
        self.assertEqual(restored, lst)

    def test_lockable_dict_pickle_and_copy(self) -> None:
        """LockableDictのpickle化およびcopyのテスト。"""
        d = LockableDict({"a": 1, "b": 2})
        d.custom_attr = "test"  # インスタンス属性の保持確認  # type: ignore

        # pickle のテスト
        dumped = pickle.dumps(d)
        restored: LockableDict[str, int] = pickle.loads(dumped)
        self.assertEqual(restored, d)
        self.assertEqual(getattr(restored, "custom_attr", None), "test")
        self.assertIsNot(restored._lock, d._lock)  # 新しいRLockが割り当てられていること

        # copy / deepcopyのテスト
        copied = copy.copy(d)
        deepcopy = copy.deepcopy(d)
        self.assertEqual(copied, d)
        self.assertEqual(deepcopy, d)
        self.assertIsNot(copied._lock, d._lock)
        self.assertIsNot(deepcopy._lock, d._lock)

    def test_lockable_list_pickle_and_copy(self) -> None:
        """LockableList の pickle 化およびcopyのテスト。"""
        lst = LockableList([1, 2, 3])
        lst.custom_attr = "test"  # type: ignore

        # pickleのテスト
        dumped = pickle.dumps(lst)
        restored: LockableList[int] = pickle.loads(dumped)
        self.assertEqual(restored, lst)
        self.assertEqual(getattr(restored, "custom_attr", None), "test")
        self.assertIsNot(restored._lock, lst._lock)

        # copy / deepcopy のテスト
        copied = copy.copy(lst)
        deepcopy = copy.deepcopy(lst)
        self.assertEqual(copied, lst)
        self.assertEqual(deepcopy, lst)
        self.assertIsNot(copied._lock, lst._lock)
        self.assertIsNot(deepcopy._lock, lst._lock)


if __name__ == "__main__":
    unittest.main()
