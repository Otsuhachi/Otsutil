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
    - [機能](#機能)
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

### 機能

#### フォルダ選択ダイアログから Path オブジェクトを取得

<details>

`choice_dir(title=None)`<br>
ディレクトリ選択ダイアログを表示し、選択されたディレクトリの`Path`を返します。<br>
ディレクトリが選択されなかった場合、呼び出し元オブジェクトの`Path`返ります。

- title: ダイアログのタイトルです。

</details>

#### ファイル選択ダイアログから Path オブジェクトを取得

<details>

`choice_file(*types, title=None, multi=False, strict=True)`<br>
ファイル選択ダイアログを表示し、選択されたファイルの`Path`を返します。

- types(str): 拡張子でフィルターを掛けることができます。
  `*.bin`ファイルだけ選択できるようにするためには`bin`を設定してください。
  複数設定すると、フィルターを追加できます。
- title(str): ダイアログのタイトルです。
- multi(bool): True にすると、複数ファイルが選択できるようになります。
  また、戻り値が`list[Path]`に変わるので注意してください。
  これは選択されたオブジェクトが結果的に一つであっても変わりません。
- strict(bool): ファイルの選択がキャンセルされたとき、`NotSelectedError`を投げます。
  `False`にすると、例外を投げる代わりに`None`を返すようになります。

</details>

#### ファイルやフォルダの名前に使用できる文字列に変換

<details>

`create_system_name(name)`<br>
ファイル名、及びフォルダ名に使用できない文字を使用可能な文字に置き換えた文字列を返します。

- name(str): ファイル名、フォルダ名に使用したい文字列です。

</details>

#### 外部ファイルからオブジェクトを読み込む

<details>

`load_object(file)`<br>
外部ファイルからオブジェクトを読み込みます。<br>
この関数は[save_object](#%e5%a4%96%e9%83%a8%e3%83%95%e3%82%a1%e3%82%a4%e3%83%ab%e3%81%ab%e3%82%aa%e3%83%96%e3%82%b8%e3%82%a7%e3%82%af%e3%83%88%e3%82%92%e4%bf%9d%e5%ad%98%e3%81%99%e3%82%8b)で保存したオブジェクトの読み込みを想定しています。<br><br>
ファイルに保存されているオブジェクトは`単一`である必要があります。<br>
複数のオブジェクトを扱いたい場合は、[pickle_dict](#pickle_dict)を使用してください。

- file(str or Path): 読み込むファイルです。

</details>

#### 外部ファイルにオブジェクトを保存する

<details>

`save_object(obj, file, protocol=4)`<br>
オブジェクトを外部ファイルに保存します。<br>
`pickle`で保存できないオブジェクトには未対応です。<br>
読み込みには[load_object](#%e5%a4%96%e9%83%a8%e3%83%95%e3%82%a1%e3%82%a4%e3%83%ab%e3%81%8b%e3%82%89%e3%82%aa%e3%83%96%e3%82%b8%e3%82%a7%e3%82%af%e3%83%88%e3%82%92%e8%aa%ad%e3%81%bf%e8%be%bc%e3%82%80)の使用を想定しています。<br><br>
この関数で保存されるオブジェクトは`単一`です。<br>
複数のオブジェクトを扱いたい場合は、[pickle_dict](#pickle_dict)を使用してください。

- obj(object): 保存したいオブジェクトです。
- file(str or Path): 書き出し先のファイルです。
- protocol(int): `pickle`で使用するプロトコルです。

</details>

#### リスト等から重複を取り除いて 1 行ずつ外部ファイルに書き出す

<details>

`write_set_lines(list_, file)`<br>
重複の不要なオブジェクト群を外部ファイルに 1 行ずつ書き出します。<br>
フォルダに含まれているファイルの拡張子一覧を書き出したいなど、ユーザーが読むための出力を想定しています。

- list\_(iter): ユーザー向けの出力をしたい iter オブジェクトです。
- file(str or Path): 出力先ファイルです。

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
