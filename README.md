# otsutil

よく使う自作関数、クラスを纏めたパッケージです。
発生したトラブル等に当方は一切責任を負いません。
仕様は自己責任でお願いします。

## 目次

<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [otsutil](#otsutil)
  - [目次](#目次)
  - [インストール](#インストール)
    - [pip](#pip)
    - [pipenv](#pipenv)
- [モジュール](#モジュール)
  - [funcs](#funcs)
    - [概要](#概要)
    - [フォルダ選択ダイアログから Path オブジェクトを取得](#フォルダ選択ダイアログから-path-オブジェクトを取得)
    - [ファイル選択ダイアログから Path オブジェクトを取得](#ファイル選択ダイアログから-path-オブジェクトを取得)
    - [ファイルやフォルダの名前に使用できる文字列に変換](#ファイルやフォルダの名前に使用できる文字列に変換)
    - [外部ファイルからオブジェクトを読み込む](#外部ファイルからオブジェクトを読み込む)
    - [外部ファイルにオブジェクトを保存する](#外部ファイルにオブジェクトを保存する)
    - [リスト等から重複を取り除いて 1 行ずつ外部ファイルに書き出す](#リスト等から重複を取り除いて-1-行ずつ外部ファイルに書き出す)
  - [pickle_dict](#pickle_dict)
    - [概要](#概要-1)
- [制作環境](#制作環境)

<!-- /code_chunk_output -->

## インストール

### pip

<details open><summary>インストール</summary>

```Console
pip install git+https://github.com/Otsuhachi/otsutil#egg=otsutil
```

</details>

<details open><summary>更新</summary>

```Console
pip install git+https://github.com/Otsuhachi/otsutil#egg=otsutil -U
```

</details>

<details><summary>アンインストール</summary>

```Console
pip uninstall otsutil
```

</details>

### pipenv

<details open><summary>インストール</summary>

```Console
pipenv install git+https://github.com/Otsuhachi/otsutil#egg=otsutil
```

</details>
<details open><summary>更新</summary>

```Console
pipenv update otsutil
```

</details>
<details><summary>アンインストール</summary>

```Console
pipenv uninstall otsutil
```

</details>

# モジュール

## funcs

### 概要

自作関数を纏めたモジュールです。

### フォルダ選択ダイアログから Path オブジェクトを取得

<details>

`choice_dir()`<br>
ディレクトリ選択ダイアログを表示し、選択されたディレクトリの`Path`を返します。<br>
ディレクトリが選択されなかった場合、呼び出し元ディレクトリの`Path`が返ります。

</details>

### ファイル選択ダイアログから Path オブジェクトを取得

<details>

`choice_file(multi=False, *, strict=True)`<br>
ファイル選択ダイアログを表示し、選択されたファイルの`Path`を返します。<br><br>
`multi`を`True`にすると、選択されたファイル群の`list[Path]`を返します。<br>
これは、ファイルが一つしか選択されていない場合でも同様なので、注意してください。<br><br>
ファイルが選択されなかった場合、`NotSelectedError`が投げられます。<br>
`strict=False`すると、例外を投げる代わりに`None`を返すようになります。

</details>

### ファイルやフォルダの名前に使用できる文字列に変換

<details>

`create_system_name(name)`<br>
`name`に与えた文字列からファイル名、及びフォルダ名に使用できない文字を使用可能な文字に置き換えた文字列を返します。

</details>

### 外部ファイルからオブジェクトを読み込む

<details>

`load_object(file)`<br>
`file`に与えられた文字列、または Path を基に外部ファイルを読み込み、保存されたオブジェクトを返します。<br>
この時、`file`に保存されているオブジェクトは`単一であることが保証されている`必要があります。<br>
[save_object](#%e5%a4%96%e9%83%a8%e3%83%95%e3%82%a1%e3%82%a4%e3%83%ab%e3%81%ab%e3%82%aa%e3%83%96%e3%82%b8%e3%82%a7%e3%82%af%e3%83%88%e3%82%92%e4%bf%9d%e5%ad%98%e3%81%99%e3%82%8b)で保存したオブジェクトを読み込むことが主な用途です。<br><br>
複数のオブジェクトを扱いたい場合は[pickle_dict](#pickledict)を使用してください。

</details>

### 外部ファイルにオブジェクトを保存する

<details>

`save_object(obj, file, protocol=4)`<br>
`file`に与えられた文字列、または Path をファイルとして扱い、`obj`に与えられたオブジェクトを`pickle_to_base64`で書き出します。<br>
この時、`protocol`を指定することで pickle での protocol を変更することができます。<br>
読み込むときは[load_object](#%e5%a4%96%e9%83%a8%e3%83%95%e3%82%a1%e3%82%a4%e3%83%ab%e3%81%8b%e3%82%89%e3%82%aa%e3%83%96%e3%82%b8%e3%82%a7%e3%82%af%e3%83%88%e3%82%92%e8%aa%ad%e3%81%bf%e8%be%bc%e3%82%80)を使用することが想定されています。
複数のオブジェクトを扱いたい場合は[pickle_dict](#pickledict)を使用してください。

</details>

### リスト等から重複を取り除いて 1 行ずつ外部ファイルに書き出す

<details>

`write_set_lines(list, file)`<br>
`list_`に与えられた`__iter__`可能オブジェクトを`file`に 1 行ずつ書き出します。<br>
書き出す際、重複するオブジェクトは 1 つを残し取り除かれます。<br>
全てのオブジェクトは`str()`されてから書き出されるので、オブジェクトの型によっては内容を把握できない型の出力になります。<br>
重複が不要なログなどを書き出す用途を想定しています。<br>
`file`が既に存在する場合は、1 行ずつ読み込んだ文字列を`list_`の先頭に追加してから出力を行います。

</details>

## pickle_dict

### 概要

このモジュールでは`pickle`でのオブジェクト管理を`辞書オブジェクト風`に行えるようにする為の PDict クラスを定義しています。<br><br>
※このモジュールは現在制作中です。
import しても開発中の旨が表示される以外に何も起こりません。

# 制作環境

- バージョン情報
  - プロセッサ
    `Intel(R) Core(TM) i7-3630QM CPU @ 2.40GHz 2.40GHz`
  - 実装 RAM
    `8.00GB (7.88GB 使用可能)`
  - システムの種類
    `64 ビットオペレーティングシステム、x64 ベースプロセッサ`
- Windows の仕様
  - エディション
    `Windows 10 Home`
  - バージョン
    `1809`
  - OS ビルド
    `17763.864`
