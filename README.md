# otsutil

よく使う関数やクラスを纏めたライブラリです。

このライブラリは以下の環境で作成・最適化されています。
`Windows10/11`, `Python 3.12.0+`

## インストール

インストール
`pip install otsutil`

アップデート
`pip install -U otsutil`

アンインストール
`pip uninstall otsutil`

## モジュール

以下のモジュールが存在します。

| モジュール名 | 概要 |
| :---: | :--- |
| [cfg](#cfgモジュール) | 定数 |
| [classes](#classesモジュール) | スレッドセーフなコンテナやタイマーなどのクラス定義 |
| [exceptions](#exceptionsモジュール) | 例外 |
| [funcs](#funcsモジュール) | ファイル操作や型判定などの便利な関数定義 |
| [types](#typesモジュール) | パッケージ全体で共通利用する型ヒント・ジェネリクス共通定義 |

---

### cfgモジュール

cfgモジュールでは以下の定数が定義されています。

| 定数名 | 概要 |
| :--: |:--- |
| **JST** | 日本のタイムゾーン。 |

---

### classesモジュール

classesモジュールでは以下のクラスが定義されています。

| クラス名 | 概要 |
| :---: | :--- |
| **LockableDict** | 要素の操作時に `threading.RLock` を使用するスレッドセーフな `dict` クラス。<br>`with obj:` 構文によるコンテキストマネージャに対応し、複数の操作をアトミックに実行可能です。 |
| **LockableList** | 要素の操作時に `threading.RLock` を使用するスレッドセーフな `list` クラス。<br>`with obj:` 構文によるコンテキストマネージャに対応し、複数の操作をアトミックに実行可能です。 |
| **ObjectStore** | オブジェクトを `pickle` + `base64` でシリアライズし、ファイルに永続化・管理するクラス。<br>カスタムクラスを保存する場合、そのクラスに `__reduce__` を実装することでリスト内の要素なども含め高度な変換・復元が可能です。 |
| **OtsuNone** | `None` を返す可能性のある辞書の `get` デフォルト値などに使用するセンチネルオブジェクト。<br>`bool()` 判定では `False` を返します。 |
| **Timer** | 指定時間の経過判定および待機を行うタイマー。<br>同期的なブロック待機 (`join`) に加え、`asyncio` による非同期待機 (`ajoin`) をサポート。<br>`for` / `async for` 文で残り時間を `yield` しながら処理を行うイテレータ機能を持ちます。 |

---

### exceptionsモジュール

exceptionsモジュールでは以下の定数が定義されています。

| 例外名 | 概要 |
| PathError | パスに関連するエラー |
| PathTypeError | パスの形式に関連するエラー |

---

### funcsモジュール

funcsモジュールでは以下の関数が定義されています。

| 関数名 | 概要 |
| :---: | :--- |
| **deduplicate** | シーケンスから重複を取り除き、順序を保持したまま元の型（`list`/`tuple`）で返す。 |
| **get_sub_paths** | ディレクトリ内を探索し、ワイルドカードや拡張子による高度なフィルタリングを適用して子パスを一覧取得する。 |
| **is_all_type** | 反復可能オブジェクトの全ての要素が、指定した型であるか判定する。 |
| **is_dict_key_type** | `dict[K, Any]`か検証する。 |
| **is_dict_type** | `dict[K, V]`か検証する。 |
| **is_dict_value_type** | `dict[K, V]`か検証する。 |
| **is_type** | オブジェクトが指定した型であるか判定する（`None` 許容判定などを含む）。 |
| **iter_sub_paths** | `get_sub_paths`のイテレータ版。 |
| **load_json** | `JSON` ファイルを読み込む。親ディレクトリがない場合は作成し、ファイルがない場合はデフォルト値を返します。 |
| **read_lines** | ファイルを1行ずつ読み出すジェネレータ。改行コードの自動除去やエンコーディング指定が可能です。 |
| **same_path** | 2つのパスが（相対/絶対に関わらず）物理的に同じ場所を指しているか判定する。 |
| **save_json** | オブジェクトを `JSON` 形式で保存する。 |
| **setup_path** | パスを `Path` オブジェクトとして整備し、必要に応じて親ディレクトリを生成して利用可能な状態にする。 |
| **str_to_path** | 文字列を `pathlib.Path` に変換する。 |
| **write_lines** | 反復可能な文字列データを1行ずつファイルに書き出す。 |

---

### typesモジュール

typesモジュールでは、Python 3.12 のジェネリクス構文に対応した以下の型定義がされています。

| 名称 | 概要 |
| :---: | :--- |
| **ExpectType[T]** | `isinstance(obj, ExpectType)`で使用できる型。 |
| **FloatInt** | `float` または `int` に限定した数値型。 |
| **HMSTuple** | `(時, 分, 秒)` のタプル。型は `(int, int, float)`。 |
| **OptPath** | `pathlib.Path` または`None` |
| **OptStrPath** | `pathlib.Path`または`str`または`None` |
| **StrPath** | `pathlib.Path` または `str`。 |
