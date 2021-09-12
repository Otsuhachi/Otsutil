- [概要](#概要)
  - [インストール](#インストール)
  - [モジュール](#モジュール)


# 概要

よく使う関数やクラスを纏めたライブラリです。  

このライブラリは以下の環境で作成されています。  
`Windows10(64bit)`, `Python3.9.6`  
`@overload`を使用しているので、`3.5`以前のバージョンでは使えません。

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

<!-- omit in toc -->
### classesモジュール

classesモジュールでは以下のクラスが定義されています。

クラス名|概要
:--:|:--
ObjectSaver|`pickle`でシリアライズ可能なオブジェクトをファイルで扱うクラス
OtsuNoneType|`None`のような何か<br>`None`を返す可能性のある`dict`で`get`するときの`default`などに使う<br>`OtsuNone`という変数があるので基本的にはそちらをインポートして使う

<!-- omit in toc -->
### funcsモジュール

funcsモジュールでは以下の関数が定義されています。

関数名|概要
:--:|:--
deduplicate|タプルやリストから重複を取り除き、順番を保持し、元の型で返す
load_json|ファイルに保存された`JSON`を読み込む<br>`open`せずにファイルを渡すことができ、指定しない場合の`encoding`が`utf-8`になる
read_lines|ファイルを読み込み1行ずつ返すジェネレータを生成する<br>行右端の改行を除去し、`open`せずにファイルを渡すことができ、指定しない場合の`encoding`が`utf-8`になる
save_json|ファイルに`JSON`を保存する。<br>`open`せずにファイルを渡すことができ、指定しない場合の`encoding`が`utf-8`になる
setup_path|親ディレクトリの存在を確認、生成、保証し、パスを返す<br>ディレクトリならば生成され、ファイルなら`open(file, 'w')`で生成可能な状態になる
write_lines|ファイルに`lines`を1行ずつ書き出す<br>`open`せずにファイルを渡すことができ、指定しない場合の`encoding`が`utf-8`になる
