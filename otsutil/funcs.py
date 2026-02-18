"""よく使う関数を纏めたモジュールです。"""

__all__ = (
    "deduplicate",
    "ensure_relative",
    "get_sub_paths",
    "get_value",
    "is_all_type",
    "is_type",
    "load_json",
    "read_lines",
    "same_path",
    "save_json",
    "setup_path",
    "str_to_path",
    "write_lines",
)


import fnmatch
import json
from collections import deque
from collections.abc import Callable, Hashable, Iterable, Iterator, Sequence
from pathlib import Path
from typing import Any, TypeGuard, overload

from .types import StrPath


@overload
def deduplicate[T](values: deque[T]) -> deque[T]: ...


@overload
def deduplicate[T](values: list[T]) -> list[T]: ...


@overload
def deduplicate[T](values: tuple[T, ...]) -> tuple[T, ...]: ...


def deduplicate[T](values: Sequence[T]) -> Sequence[T]:
    """シーケンスから重複を取り除きます。

    順番を保持しつつ重複を除去します。
    元の型(deque, list, tuple)を維持して返します。それ以外は list を返します。

    Args:
        values (Sequence[T]): 重複を取り除きたいシーケンス。

    Returns:
        Sequence[T]: 重複を除去した、入力と同じ型(またはlist)のシーケンス。
    """
    res = list(dict.fromkeys(values))
    if isinstance(values, tuple):
        return tuple(res)
    if isinstance(values, deque):
        return deque(res)
    return res


def get_value[T](
    data: dict[Any, Any],
    key: Hashable,
    type_: type[T],
    factory: Callable[[], T] | None = None,
    set_none_on_exception: bool = True,
) -> T | None:
    """辞書から値を取得します。値が存在しない場合は生成して登録します。

    Args:
        data (dict[Any, Any]): 取得元の辞書。
        key (Hashable): 取得するキー。
        type_ (type[T]): 期待する値の型。
        factory (Callable[[], T] | None, optional): 値がなかった時の生成用関数。
            指定がない場合は type_() が呼ばれます。 Defaults to None.
        set_none_on_exception (bool, optional): 型チェックに通らなかった際、
            None で辞書を上書きするかどうか。 Defaults to True.

    Raises:
        TypeError: 取得または生成した値が type_ と一致せず、
            set_none_on_exception が False の場合に投げられます。

    Returns:
        T | None: 取得または生成された値。型不一致時は None。
    """
    sentinel = object()
    res = data.get(key, sentinel)
    is_defined = res is not sentinel
    if not is_defined:
        # キーがない場合のみファクトリを実行
        f = factory if factory is not None else type_
        try:
            res = f()
        except Exception:
            res = None

    is_valid = is_type(res, type_, use_isinstance=False) or is_type(
        res, type_, use_isinstance=True
    )
    if not is_valid:
        if set_none_on_exception:
            data[key] = None
            return None
        msg = f"{key}で取得した値は{type_}型ではありませんでした。({res})"
        raise TypeError(msg)
    if not is_defined:
        data[key] = res
    return res


def is_all_type[T](
    seq: Sequence[Any],
    type_: type[T],
    use_isinstance: bool = False,
) -> TypeGuard[Sequence[T]]:
    """シーケンスのすべての要素に対して型判定を行います。

    Args:
        seq (Sequence[Any]): 対象のシーケンス。
        type_ (type[T]): 期待する型。
        use_isinstance (bool, optional): isinstance を使用して判定するか。
            False の場合は type(obj) is type_ で判定します。 Defaults to False.

    Returns:
        TypeGuard[Sequence[T]]: すべての要素が指定した型であるかどうかの結果。
    """
    return all(is_type(x, type_, use_isinstance) for x in seq)


def is_type[T](
    obj: Any,  # noqa: ANN401
    type_: type[T],
    use_isinstance: bool = False,
) -> TypeGuard[T]:
    """オブジェクトの型判定を行います。

    Args:
        obj (Any): 判定対象のオブジェクト。
        type_ (type[T]): 期待する型。
        use_isinstance (bool, optional): isinstance を使用して判定するか。
            False の場合は type(obj) is type_ で判定します。 Defaults to False.

    Returns:
        TypeGuard[T]: 指定した型であるかどうかの結果。
    """
    actual_type = type(None) if type_ is None else type_
    if use_isinstance:
        return isinstance(obj, actual_type)
    return type(obj) is actual_type


def load_json(
    file: StrPath,
    encoding: str = "utf-8",
    **kwargs: Any,
) -> dict[Any, Any] | list[Any]:
    """JSON形式のファイルを読み込みます。

    Args:
        file (StrPath): 読み込むJSONファイルのパス。
        encoding (str, optional): ファイルのエンコーディング。 Defaults to "utf-8".
        **kwargs (Any): json.load に渡される追加のキーワード引数。

    Raises:
        FileNotFoundError: 指定されたパスが存在しないか、ファイルでない場合に投げられます。

    Returns:
        dict[Any, Any] | list[Any]: 読み込まれたJSONデータ。
    """
    path = str_to_path(file)
    if not path.is_file():
        msg = f"{path}は存在しないかファイルではありません。"
        raise FileNotFoundError(msg)
    with path.open("r", encoding=encoding) as f:
        kwargs["fp"] = f
        return json.load(**kwargs)


def read_lines(
    file: StrPath,
    ignore_blank_line: bool = False,
    encoding: str = "utf-8",
    **kwargs: Any,
) -> Iterator[str]:
    """ファイルを読み込み、1行ずつ返すイテレータを生成します。

    各行の右端にある改行コードは自動的に除去されます。

    Args:
        file (StrPath): 読み込むファイルのパス。
        ignore_blank_line (bool, optional): 空白行（stripして空になる行）を無視するかどうか。
            Defaults to False.
        encoding (str, optional): ファイルのエンコーディング。 Defaults to "utf-8".
        **kwargs (Any): Path.open に渡される追加のキーワード引数。modeは 'r' 固定です。

    Raises:
        FileNotFoundError: 指定されたパスが存在しないか、ファイルでない場合に投げられます。

    Yields:
        Iterator[str]: ファイルの各行の内容。
    """
    path = str_to_path(file)
    if not path.is_file():
        msg = f"{path}は存在しないかファイルではありません。"
        raise FileNotFoundError(msg)
    kwargs["encoding"] = encoding
    if "file" in kwargs:
        del kwargs["file"]
    kwargs["mode"] = "r"
    with path.open(**kwargs) as f:
        gen = map(lambda x: x.rstrip("\n"), f)
        if ignore_blank_line:
            gen = filter(lambda x: x.strip(), gen)
        yield from gen


def same_path(p1: StrPath, p2: StrPath) -> bool:
    """2つのパスが実体として同一かどうかを判定します。

    Args:
        p1 (StrPath): 比較するパス1。
        p2 (StrPath): 比較するパス2。

    Returns:
        bool: 同一のパスであれば True、そうでなければ False。
    """
    return str_to_path(p1).resolve() == str_to_path(p2).resolve()


def save_json(
    file: StrPath,
    data: dict[Any, Any] | list[Any],
    encoding: str = "utf-8",
    ensure_ascii: bool = False,
    indent: int | str | None = 4,
    sort_keys: bool = True,
    **kwargs: Any,
) -> None:
    """指定したファイルにデータをJSON形式で書き出します。

    Args:
        file (StrPath): 出力先のファイルパス。
        data (dict[Any, Any] | list[Any]): 書き出すデータ。
        encoding (str, optional): ファイルのエンコーディング。 Defaults to "utf-8".
        ensure_ascii (bool, optional): json.dump の ensure_ascii 引数。 Defaults to False.
        indent (int | str | None, optional): json.dump の indent 引数。 Defaults to 4.
        sort_keys (bool, optional): json.dump の sort_keys 引数。 Defaults to True.
        **kwargs (Any): json.dump に渡される追加のキーワード引数。
    """
    path = setup_path(file)
    with path.open("w", encoding=encoding) as f:
        kwargs["fp"] = f
        kwargs["obj"] = data
        kwargs["ensure_ascii"] = ensure_ascii
        kwargs["indent"] = indent
        kwargs["sort_keys"] = sort_keys
        json.dump(**kwargs)


def ensure_relative(path: StrPath, base: StrPath) -> Path:
    """パスを基準ディレクトリからの相対パスに変換します。

    絶対パスが渡された場合、基準ディレクトリからの相対パスに解決します。
    既に相対パスである場合はそのまま Path オブジェクトとして返します。
    基準ディレクトリの外にある絶対パスが渡された場合、解決不能として ValueError を投げることがあります。

    Args:
        path (StrPath): 変換対象のパス。
        base (StrPath): 基準となるディレクトリのパス。

    Returns:
        Path: 相対パス化された Path オブジェクト。
    """
    p = str_to_path(path)
    if not p.is_absolute():
        return p
    return p.relative_to(str_to_path(base).resolve())


def get_sub_paths(
    root: StrPath,
    recursive: bool = True,
    include_exts: list[str] | None = None,
    include_names: list[str] | None = None,
    exclude_names: list[str] | None = None,
    only_file: bool = False,
    only_dir: bool = False,
) -> list[Path]:
    """ディレクトリ内の子パスをフィルタリングして一括取得します。

    Args:
        root (StrPath): 探索先のルートディレクトリ。
        recursive (bool, optional): 再帰的に探索するかどうか。 Defaults to True.
        include_exts (list[str] | None, optional): 抽出する拡張子のリスト（例: [".py"]）。
            内部的には include_names のショートカットとして機能します。 Defaults to None.
        include_names (list[str] | None, optional): 抽出する名前のパターン（ワイルドカード可）。 Defaults to None.
        exclude_names (list[str] | None, optional): 除外する名前のパターン（ワイルドカード可）。 Defaults to None.
        only_file (bool, optional): ファイルのみを抽出するか。 Defaults to False.
        only_dir (bool, optional): ディレクトリのみを抽出するか。 Defaults to False.

    Returns:
        list[Path]: 抽出されたパスのリスト。

    Raises:
        NotADirectoryError: 指定された root がディレクトリでない場合に投げられます。
    """
    root_path = str_to_path(root)
    if not root_path.is_dir():
        msg = f"{root_path}はディレクトリではないか、存在しません。"
        raise NotADirectoryError(msg)

    pattern = "**/*" if recursive else "*"
    all_paths = root_path.glob(pattern)

    # フィルタロジックの構築と正規化
    i_names = set(include_names or [])
    if include_exts:
        for ext in include_exts:
            # ".txt", "txt", "*.txt" をすべて "*.txt" に正規化
            clean_ext = ext.removeprefix("*").removeprefix(".")
            i_names.add(f"*.{clean_ext}")

    e_names = set(exclude_names or [])

    res = []
    for p in all_paths:
        if only_file and not p.is_file():
            continue
        if only_dir and not p.is_dir():
            continue

        name = p.name
        # 包含フィルタ（一つでも一致すれば通過）
        if i_names and not any(fnmatch.fnmatch(name, pat) for pat in i_names):
            continue
        # 除外フィルタ（一つでも一致すれば脱落）
        # 包含フィルタを通過した後でも、除外にヒットすれば追加されません。
        if e_names and any(fnmatch.fnmatch(name, pat) for pat in e_names):
            continue

        res.append(p)

    return res


def setup_path(path: StrPath, is_dir: bool = False) -> Path:
    """親ディレクトリの存在を保証し、Pathオブジェクトを返します。

    Args:
        path (StrPath): セットアップしたいパス。
        is_dir (bool, optional): 指定したパス自体をディレクトリとして作成するかどうか。
            False の場合はその親ディレクトリを作成します。 Defaults to False.

    Returns:
        Path: セットアップされたPathオブジェクト。
    """
    p = str_to_path(path)
    target = p if is_dir else p.parent
    if not target.exists():
        target.mkdir(parents=True)
    return p


def str_to_path(path: StrPath) -> Path:
    """パス（文字列またはPath）をPathオブジェクトに変換します。

    Args:
        path (StrPath): 変換対象のパス。

    Returns:
        Path: Pathオブジェクト。
    """
    return path if isinstance(path, Path) else Path(path)


def write_lines(
    file: StrPath,
    lines: Iterable[Any],
    add_blank_line: bool = False,
    encoding: str = "utf-8",
    **kwargs: Any,
) -> None:
    """ファイルにIterableの各要素を1行ずつ書き出します。

    Args:
        file (StrPath): 出力先のファイルパス。
        lines (Iterable[Any]): 書き出す内容のイテラブル。各要素は str に変換されます。
        add_blank_line (bool, optional): ファイルの末尾を空白行で終わらせるかどうか。
            Defaults to False.
        encoding (str, optional): ファイルのエンコーディング。 Defaults to "utf-8".
        **kwargs (Any): Path.open に渡される追加のキーワード引数。modeは 'w' 固定です。
    """
    path = setup_path(file)
    kwargs["encoding"] = encoding
    kwargs["mode"] = "w"
    kwargs.pop("file", None)
    with path.open(**kwargs) as f:
        last_line = ""
        for i, line in enumerate(map(str, lines)):
            if i > 0:
                f.write("\n")
            f.write(line)
            last_line = line
        if add_blank_line and last_line.strip():
            f.write("\n")
