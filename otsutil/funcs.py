"""よく使う関数を纏めたモジュール。"""

__all__ = [
    "deduplicate",
    "get_sub_paths",
    "is_all_type",
    "is_dict_key_type",
    "is_dict_type",
    "is_dict_value_type",
    "is_type",
    "iter_sub_paths",
    "load_json",
    "read_lines",
    "same_path",
    "save_json",
    "setup_path",
    "str_to_path",
    "write_lines",
]


import fnmatch
import json
from collections import deque
from collections.abc import Collection, Iterable, Iterator, Sequence
from pathlib import Path
from typing import Any, Literal, Never, TypeGuard, overload

from .exceptions import PathTypeError
from .types import ExpectType, OptPath, OptStrPath, StrPath


@overload
def deduplicate[T](values: frozenset[T]) -> frozenset[T]: ...  # type: ignore[overload-overlap]


@overload
def deduplicate[T](values: set[T]) -> set[T]: ...


@overload
def deduplicate[T](values: tuple[T, ...]) -> tuple[T, ...]: ...


@overload
def deduplicate[T](values: deque[T]) -> deque[T]: ...


@overload
def deduplicate(values: str) -> Never: ...


@overload
def deduplicate[T](values: Iterable[T]) -> list[T]: ...


def deduplicate[T](values: Iterable[T]) -> Iterable[T]:
    """Iterableから重複を取り除く。
    文字列は処理できない。

    `set(values)`と違い順番を保持する。
    一部の型は元の型を保持し、それ以外の型はlist[T]として返す。

    Args:
        values (Iterable[T]): 重複を取り除きたいIterable。

    Raises:
        TypeError: 文字列が渡された場合。

    Returns:
        Iterable[T]: 重複を除去したIterable。
    """
    if isinstance(values, str):
        msg = "文字列から重複を取り除くことはできません。"
        raise TypeError(msg)

    res = list(dict.fromkeys(values))

    if isinstance(values, frozenset):
        return frozenset(res)
    if isinstance(values, set):
        return set(res)
    if isinstance(values, tuple):
        return tuple(res)
    if isinstance(values, deque):
        return deque(res)

    return res


def get_sub_paths(
    root: StrPath,
    recursive: bool = True,
    include_exts: Iterable[str] | None = None,
    include_names: Iterable[str] | None = None,
    exclude_names: Iterable[str] | None = None,
    only_file: bool = False,
    only_dir: bool = False,
) -> list[Path]:
    """ディレクトリ内の子パスをフィルタリングして一括取得する。

    Args:
        root (StrPath): 探索先のルートディレクトリ。
        recursive (bool, optional): 再帰的に探索するか。 Defaults to True.
        include_exts (Iterable[str] | None, optional): 抽出する拡張子のリスト。 Defaults to None.
        include_names (Iterable[str] | None, optional): 抽出する名前のパターン（ワイルドカード可）。 Defaults to None.
        exclude_names (Iterable[str] | None, optional): 除外する名前のパターン（ワイルドカード可）。 Defaults to None.
        only_file (bool, optional): ファイルのみを抽出するか。 Defaults to False.
        only_dir (bool, optional): ディレクトリのみを抽出するか。 Defaults to False.

    Raises:
        ValueError: `only_file`, `only_dir`を両方Trueにした場合。
        PathTypeError: `root.is_dir()`がFalseの場合。

    Returns:
        list[Path]: 抽出したパス。
    """
    return list(
        iter_sub_paths(
            root=root,
            recursive=recursive,
            include_exts=include_exts,
            include_names=include_names,
            exclude_names=exclude_names,
            only_file=only_file,
            only_dir=only_dir,
        )
    )


@overload
def is_all_type[T](itr: deque[Any], expect_type: ExpectType[T], use_isinstance: bool = True) -> TypeGuard[deque[T]]: ...


@overload
def is_all_type[T](itr: list[Any], expect_type: ExpectType[T], use_isinstance: bool = True) -> TypeGuard[list[T]]: ...


@overload
def is_all_type[T](itr: set[Any], expect_type: ExpectType[T], use_isinstance: bool = True) -> TypeGuard[set[T]]: ...


@overload
def is_all_type[T](itr: tuple[Any, ...], expect_type: ExpectType[T], use_isinstance: bool = True) -> TypeGuard[tuple[T, ...]]: ...


@overload
def is_all_type[T](itr: frozenset[Any], expect_type: ExpectType[T], use_isinstance: bool = True) -> TypeGuard[frozenset[T]]: ...


@overload
def is_all_type[T](itr: Sequence[Any], expect_type: ExpectType[T], use_isinstance: bool = True) -> TypeGuard[Sequence[T]]: ...


@overload
def is_all_type[T](itr: Collection[Any], expect_type: ExpectType[T], use_isinstance: bool = True) -> TypeGuard[Collection[T]]: ...


def is_all_type[T](
    itr: Collection[Any],
    expect_type: ExpectType[T],
    use_isinstance: bool = True,
) -> TypeGuard[Collection[T]]:
    """渡されたCollectionオブジェクトの中身が全て`expect_type型`であるか判定する。

    Args:
        itr (Collection[Any]): 判定対象。
        expect_type (ExpectType[T]): 対象型。
        use_isinstance (bool, optional): isinstanceを使って判定するか。 Defaults to True.

    Returns:
        TypeGuard[Collection[T]]: 判定結果。
    """
    return all(
        is_type(
            x,
            expect_type,
            use_isinstance=use_isinstance,
        )
        for x in itr
    )


def is_dict_key_type[K_in, K, V](
    dic: dict[K_in, V],
    expect_type: ExpectType[K],
    use_isinstance: bool = True,
) -> TypeGuard[dict[K, V]]:
    """辞書のキーが全て`K型`であるか検証する。

    Args:
        dic (dict[K_in, V]): 対象の辞書。
        expect_type (ExpectType[K]): 対象型。
        use_isinstance (bool): isinstanceを使って判定するか。 defaults to True.

    Returns:
        TypeGuard[dict[K, V]]: 判定結果。
    """
    return is_all_type(
        dic.keys(),
        expect_type=expect_type,
        use_isinstance=use_isinstance,
    )


def is_dict_type[K_in, V_in, K, V](
    dic: dict[K_in, V_in],
    expect_type_key: ExpectType[K],
    expect_type_value: ExpectType[V],
    use_isinstance_key: bool = True,
    use_isinstance_value: bool = True,
) -> TypeGuard[dict[K, V]]:
    """辞書のキーが全て`K型`かつ、値が全て`V型`であるか検証する。

    Args:
        dic (dict[K_in, V_in]): 対象の辞書。
        expect_type_key (ExpectType[K]): キーの対象型。
        expect_type_value (ExpectType[V]): 値の対象型。
        use_isinstance_key (bool): キーの検証をisinstanceで行うか。 defaults to True.
        use_isinstance_value (bool): 値の検証をisinstanceで行うか。 defaults to True.

    Returns:
        TypeGuard[dict[K, V]]: 判定結果。
    """
    return is_dict_key_type(
        dic,
        expect_type=expect_type_key,
        use_isinstance=use_isinstance_key,
    ) and is_dict_value_type(
        dic,
        expect_type=expect_type_value,
        use_isinstance=use_isinstance_value,
    )


def is_dict_value_type[V_in, K, V](
    dic: dict[K, V_in],
    expect_type: ExpectType[V],
    use_isinstance: bool = True,
) -> TypeGuard[dict[K, V]]:
    """辞書の値が全て`V型`であるか検証する。

    Args:
        dic (dict[K, V_in]): 対象の辞書。
        expect_type (ExpectType[V]): 対象型。
        use_isinstance (bool): isinstanceを使って判定するか。 defaults to True.

    Returns:
        TypeGuard[dict[K, V]]: 判定結果。
    """
    return is_all_type(
        dic.values(),
        expect_type=expect_type,
        use_isinstance=use_isinstance,
    )


def is_type[T](
    obj: Any,
    expect_type: ExpectType[T],
    use_isinstance: bool = True,
) -> TypeGuard[T]:
    """渡されたオブジェクトが`expect_type型`であるか判定する。

    Args:
        obj (Any): 判定対象。
        expect_type (ExpectType[T]): 対象型。
        use_isinstance (bool, optional): isinstanceを使って判定するか。 Defaults to True.

    Returns:
        TypeGuard[T]: 判定結果。
    """
    actual_type = type(None) if expect_type is None else expect_type
    if use_isinstance:
        return isinstance(obj, actual_type)
    return type(obj) in actual_type if isinstance(actual_type, tuple) else type(obj) is actual_type


def iter_sub_paths(
    root: StrPath,
    recursive: bool = True,
    include_exts: Iterable[str] | None = None,
    include_names: Iterable[str] | None = None,
    exclude_names: Iterable[str] | None = None,
    only_file: bool = False,
    only_dir: bool = False,
) -> Iterator[Path]:
    """ディレクトリ内の子パスをフィルタリングして順次取得する。

    Args:
        root (StrPath): 探索先のルートディレクトリ。
        recursive (bool, optional): 再帰的に探索するか。 Defaults to True.
        include_exts (Iterable[str] | None, optional): 抽出する拡張子のリスト。 Defaults to None.
        include_names (Iterable[str] | None, optional): 抽出する名前のパターン（ワイルドカード可）。 Defaults to None.
        exclude_names (Iterable[str] | None, optional): 除外する名前のパターン（ワイルドカード可）。 Defaults to None.
        only_file (bool, optional): ファイルのみを抽出するか。 Defaults to False.
        only_dir (bool, optional): ディレクトリのみを抽出するか。 Defaults to False.

    Raises:
        ValueError: `only_file`, `only_dir`を両方Trueにした場合。
        PathTypeError: `root.is_dir()`がFalseの場合。

    Yields:
        Iterator[Path]: 抽出したパス。
    """
    if only_file and only_dir:
        msg = "`only_file`と`only_dir`は同時に`True`に指定できません。"
        raise ValueError(msg)

    root_path = str_to_path(root)
    if not root_path.is_dir():
        msg = f"{root_path}はディレクトリではないか、存在しません。"
        raise PathTypeError(msg)

    i_names = set(include_names or [])
    if include_exts:
        for ext in include_exts:
            clean_ext = ext.removeprefix("*").removeprefix(".")
            i_names.add(f"*.{clean_ext}")

    e_names = set(exclude_names or [])

    def _is_match(path: Path, patterns: set[str]) -> bool:
        name = path.name
        return any(fnmatch.fnmatch(name, pat) or path.match(pat) for pat in patterns)

    def _should_include(path: Path) -> bool:
        if i_names and not _is_match(path, i_names):
            return False

        return not (e_names and _is_match(path, e_names))

    if not recursive:
        for p in root_path.iterdir():
            if only_file and not p.is_file():
                continue
            if only_dir and not p.is_dir():
                continue

            if _should_include(p):
                yield p

        return

    for dirpath, dirnames, filenames in root_path.walk():
        if e_names:
            dirnames[:] = [d for d in dirnames if not _is_match(dirpath / d, e_names)]

        if not only_dir:
            for fn in filenames:
                fp = dirpath / fn
                if _should_include(fp):
                    yield fp

        if not only_file:
            for dn in dirnames:
                dp = dirpath / dn
                if _should_include(dp):
                    yield dp


def load_json(
    file: StrPath,
    encoding: str = "utf-8",
    **kwargs,
) -> dict[Any, Any] | list[Any]:
    """JSON形式のファイルを読み込む。

    Args:
        file (StrPath): 読み込むJSONファイルのパス。
        encoding (str, optional): ファイルのエンコーディング。 Defaults to "utf-8".
        **kwargs (Any): json.load に渡される追加のキーワード引数。

    Raises:
        PathTypeError: `file`がディレクトリの場合。
        FileNotFoundError: `file`が存在しない場合。

    Returns:
        dict[Any, Any] | list[Any]: 読み込まれたJSONデータ。
    """
    path = str_to_path(file)
    if path.exists() and path.is_dir():
        msg = f"`{path}`がディレクトリとして存在しています。"
        raise PathTypeError(msg)
    if not path.is_file():
        msg = f"{path}はファイルではありません。"
        raise FileNotFoundError(msg)

    with path.open("r", encoding=encoding) as f:
        kwargs["fp"] = f
        return json.load(**kwargs)


def read_lines(
    file: StrPath,
    ignore_blank_line: bool = False,
    encoding: str = "utf-8",
    **kwargs,
) -> Iterator[str]:
    """ファイルを読み込み、1行ずつ返すイテレータを生成する。

    各行の右端にある改行コードは自動的に除去される。

    Args:
        file (StrPath): 読み込むファイルのパス。
        ignore_blank_line (bool, optional): 空白行（stripして空になる行）を無視するか。 Defaults to False.
        encoding (str, optional): ファイルのエンコーディング。 Defaults to "utf-8".
        **kwargs (Any): `Path.open`に渡される追加のキーワード引数。`mode`は`r`固定です。

    Raises:
        PathTypeError: `file`がディレクトリの場合。
        FileNotFoundError: `file`が存在しない場合。

    Yields:
        Iterator[str]: 各行。
    """
    path = str_to_path(file)
    if path.exists() and path.is_dir():
        msg = f"`{path}`がディレクトリとして存在しています。"
        raise PathTypeError(msg)
    if not path.is_file():
        msg = f"{path}はファイルではありません。"
        raise FileNotFoundError(msg)

    kwargs["encoding"] = encoding
    kwargs.pop("file", None)
    kwargs.pop("mode", None)

    with path.open("r", **kwargs) as f:
        gen = (x.rstrip("\n") for x in f)
        if ignore_blank_line:
            gen = filter(str.strip, gen)
        yield from gen


def same_path(p1: StrPath, p2: StrPath) -> bool:
    """2つのパスが実体として同一か判定する。

    Args:
        p1 (StrPath): 比較するパス1。
        p2 (StrPath): 比較するパス2。

    Returns:
        bool: 判定結果。
    """
    return str_to_path(p1, resolve=True) == str_to_path(p2, resolve=True)


def save_json(
    file: StrPath,
    data: dict[Any, Any] | list[Any],
    encoding: str = "utf-8",
    ensure_ascii: bool = False,
    indent: int | str | None = 4,
    sort_keys: bool = True,
    **kwargs,
) -> None:
    """指定したファイルにデータをJSON形式で書き出す。

    Args:
        file (StrPath): 出力先のファイルパス。
        data (dict[Any, Any] | list[Any]): 書き出すデータ。
        encoding (str, optional): ファイルのエンコーディング。 Defaults to "utf-8".
        ensure_ascii (bool, optional): json.dump の ensure_ascii 引数。 Defaults to False.
        indent (int | str | None, optional): json.dump の indent 引数。 Defaults to 4.
        sort_keys (bool, optional): json.dump の sort_keys 引数。 Defaults to True.
        **kwargs (Any): json.dump に渡される追加のキーワード引数。

    Raises:
        PathTypeError: `file`がディレクトリの場合。
    """
    path = setup_path(file)
    if path.exists() and path.is_dir():
        msg = f"`{path}`がディレクトリとして存在しています。"
        raise PathTypeError(msg)

    with path.open("w", encoding=encoding) as f:
        kwargs["fp"] = f
        kwargs["obj"] = data
        kwargs["ensure_ascii"] = ensure_ascii
        kwargs["indent"] = indent
        kwargs["sort_keys"] = sort_keys
        json.dump(**kwargs)


@overload
def setup_path(path: StrPath, is_dir: bool = False, resolve: bool | Literal["strict"] = False) -> Path: ...


@overload
def setup_path(path: OptPath, is_dir: bool = False, resolve: bool | Literal["strict"] = False) -> OptPath: ...


@overload
def setup_path(path: OptStrPath, is_dir: bool = False, resolve: bool | Literal["strict"] = False) -> OptPath: ...


def setup_path(
    path: OptStrPath,
    is_dir: bool = False,
    resolve: bool | Literal["strict"] = False,
) -> OptPath:
    """親ディレクトリの存在を保証し、Pathオブジェクトを返します。Noneを渡した場合はNoneを返す。

    Args:
        path (OptStrPath): セットアップしたいパス。
        is_dir (bool, optional): 指定したパス自体をディレクトリとして作成するか。 Defaults to False.
        resolve (bool | Literal[&quot;strict&quot;], optional): `Path.resolve`をするか。 Defaults to False.

    Returns:
        OptPath: セットアップされたパス。
    """
    p = str_to_path(path=path, resolve=resolve)
    if p is None:
        return p

    target = p if is_dir else p.parent
    if not target.exists():
        target.mkdir(parents=True)

    return p


@overload
def str_to_path(path: StrPath, resolve: bool | Literal["strict"] = False) -> Path: ...


@overload
def str_to_path(path: OptPath, resolve: bool | Literal["strict"] = False) -> OptPath: ...


@overload
def str_to_path(path: OptStrPath, resolve: bool | Literal["strict"] = False) -> OptPath: ...


def str_to_path(
    path: OptStrPath,
    resolve: bool | Literal["strict"] = False,
) -> OptPath:
    """パスを取得する。Noneを渡した場合はNoneを返す。

    Args:
        path (OptStrPath): パス。
        resolve (bool | Literal[&quot;strict&quot;], optional): `Path.resolve`をするか。 Defaults to False.

    Returns:
        OptPath: パスまたはNone。
    """
    if path is None:
        return path
    if isinstance(path, str):
        path = Path(path)
    if resolve is False:
        return path
    return path.resolve(strict=True) if resolve == "strict" else path.resolve()


def write_lines(
    file: StrPath,
    lines: Iterable[Any],
    add_blank_line: bool = False,
    encoding: str = "utf-8",
    **kwargs,
) -> None:
    """ファイルにIterableの各要素を1行ずつ書き出す。

    Args:
        file (StrPath): 出力先のファイルパス。
        lines (Iterable[Any]): 書き出す内容。
        add_blank_line (bool, optional): ファイルの末尾を空白行で終わらせるか。 Defaults to False.
        encoding (str, optional): ファイルのエンコーディング。 Defaults to "utf-8".

    Raises:
        PathTypeError: `file`がディレクトリの場合。
    """
    path = setup_path(file)
    if path.exists() and path.is_dir():
        msg = f"`{path}`がディレクトリとして存在しています。"
        raise PathTypeError(msg)
    kwargs["encoding"] = encoding
    kwargs.pop("mode", None)
    kwargs.pop("file", None)
    with path.open(mode="w", **kwargs) as f:
        last_line = ""
        for i, line in enumerate([x if isinstance(x, str) else str(x) for x in lines]):
            if i > 0:
                f.write("\n")
            f.write(line)
            last_line = line

        if add_blank_line and last_line.strip():
            f.write("\n")
