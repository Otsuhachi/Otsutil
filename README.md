- [概要](#概要)
  - [インストール](#インストール)
  - [モジュール](#モジュール)


# 概要

よく使う関数やクラスを纏めたライブラリです。

このライブラリは以下の環境で作成されています。
`Windows10(64bit)`, `Python3.10.8`

## インストール

インストール
`pip install otsutil`

アップデート
`pip install -U otsutil`

アンインストール
`pip uninstall otsutil`

## モジュール

以下のモジュールが存在します。

モジュール名|概要
:--:|:--
[classes](#classesモジュール)|よく使うクラスが定義されている
[funcs](#funcsモジュール)|よく使う関数が定義されている
[types](#typesモジュール)|よく使う型ヒントが定義されている

<!-- omit in toc -->
### classesモジュール

classesモジュールでは以下のクラスが定義されています。

クラス名|概要
:--:|:--
LockableDict|要素の操作時に`threading.Lock`を使用する`dict`クラス<br>`items`, `keys`, `values`などのメソッドで生成したIteratorオブジェクトをサイズ変更後に`next`した場合に例外が起こるのはオリジナルと同様
LockableList|要素の操作時に`threading.Lock`を使用する`list`クラス
ObjectSaver|`pickle`でシリアライズ可能なオブジェクトをファイルで扱うクラス
OtsuNone|`None`のような何か<br>`None`を返す可能性のある`dict`で`get`するときの`default`などに使う<br>厳密にはクラスではなく`__OtsuNoneType`というシングルトンクラスのインスタンス
Timer|`n秒タイマー`<br>`n秒経過するまで`, `今からn秒経過するまで`, `n秒経過したか`などを判定したり<br>`for文で定期的に処理を割り込ませる`ためのメソッドなどがある

<!-- omit in toc -->
### funcsモジュール

funcsモジュールでは以下の関数が定義されています。

関数名|概要
:--:|:--
deduplicate|タプルやリストから重複を取り除き、順番を保持し、元の型で返す
load_json|ファイルに保存された`JSON`を読み込む<br>`open`せずにファイルを渡すことができ、指定しない場合の`encoding`が`utf-8`になる
read_lines|ファイルを読み込み1行ずつ返すジェネレータを生成する<br>行右端の改行を除去し、`open`せずにファイルを渡すことができ、指定しない場合の`encoding`が`utf-8`になる
same_path|パスが同一か判定する<br>相対パス、絶対パスにかかわらず開いたとき同じものであれば`True`を返す
save_json|ファイルに`JSON`を保存する。<br>`open`せずにファイルを渡すことができ、指定しない場合の`encoding`が`utf-8`になる
setup_path|親ディレクトリの存在を確認、生成、保証し、パスを返す<br>ディレクトリならば生成され、ファイルなら`open(file, 'w')`で生成可能な状態になる
str_to_path|文字列を`Path`に変換する
write_lines|ファイルに`lines`を1行ずつ書き出す<br>`open`せずにファイルを渡すことができ、指定しない場合の`encoding`が`utf-8`になる

<!-- omit in toc -->
### typesモジュール

typesモジュールでは以下の型ヒントやジェネリクスが定義されています。
名称|形式|概要
:--:|:--:|:--
FLOAT_INT|ジェネリクス|`float`または`int`に絞ったジェネリクス
K|ジェネリクス|`dict`型のキーを表す想定のジェネリクス
P|ジェネリクス|`関数の引数`を表すジェネリクス
R|ジェネリクス|`関数の戻り値`を表すジェネリクス
T|ジェネリクス|型指定もなにもないジェネリクス
V|ジェネリクス|`dict`型の値、`list`型の値を表す想定のジェネリクス
hmsValue|タイプエイリアス|(時, 分, 秒)のタプル<br>型はそれぞれ(`int`, `int`, `float`)
pathLike|タイプエイリアス|`pathlib.Path`または`str`型
