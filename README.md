# otsutil {ignore=true}

よく使う自作関数、クラスを纏めたパッケージです。

発生したトラブル等に当方は一切責任を負いません。

使用は自己責任でお願いします。

## 目次 {ignore=true}


<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

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
      - [リスト等から重複を取り除いたリストを生成する](#リスト等から重複を取り除いたリストを生成する)
      - [リスト等から重複を取り除いて 1 行ずつ外部ファイルに書き出す](#リスト等から重複を取り除いて-1-行ずつ外部ファイルに書き出す)
      - [質問を行い真偽値の回答を取得する](#質問を行い真偽値の回答を取得する)
      - [入力を受け取り指定した型に変換する](#入力を受け取り指定した型に変換する)
      - [辞書オブジェクトから例外を起こさずに値を取得する](#辞書オブジェクトから例外を起こさずに値を取得する)
      - [標準出力で進捗表示など同じ行を使いまわす](#標準出力で進捗表示など同じ行を使いまわす)
  - [pickle_dict](#pickle_dict)
    - [概要](#概要-1)
    - [使い方](#使い方)
      - [管理オブジェクトの生成](#管理オブジェクトの生成)
      - [要素の追加・変更](#要素の追加変更)
        - [add](#add)
        - [rewrite](#rewrite)
        - [辞書風に追加](#辞書風に追加)
      - [要素の削除](#要素の削除)
        - [remove](#remove)
        - [del](#del)
      - [一覧の取得・出力](#一覧の取得出力)
        - [キーと値の一覧の出力](#キーと値の一覧の出力)
        - [キー一覧の取得](#キー一覧の取得)
        - [値の一覧の取得](#値の一覧の取得)
      - [キーの存在確認](#キーの存在確認)
      - [要素数の確認](#要素数の確認)
      - [iter](#iter)
- [制作環境](#制作環境)

<!-- /code_chunk_output -->


## インストール

### pip

インストール

```Console
pip install git+https://github.com/Otsuhachi/otsutil#egg=otsutil
```

更新

```Console
pip install git+https://github.com/Otsuhachi/otsutil#egg=otsutil -U
```

アンインストール

```Console
pip uninstall otsutil
```

### pipenv

インストール

```Console
pipenv install git+https://github.com/Otsuhachi/otsutil#egg=otsutil
```

更新

```Console
pipenv update otsutil
```

アンインストール

```Console
pipenv uninstall otsutil
```

# モジュール

## funcs

### 概要

自作関数を纏めたモジュールです。

### 機能

#### フォルダ選択ダイアログから Path オブジェクトを取得

`choice_dir(title=None)`

ディレクトリ選択ダイアログを表示し、選択されたディレクトリの`Path`を返します。

ディレクトリが選択されなかった場合、呼び出し元オブジェクトの`Path`返ります。

- title: ダイアログのタイトルです。

#### ファイル選択ダイアログから Path オブジェクトを取得

`choice_file(*types, title=None, multi=False, strict=True)`

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

#### ファイルやフォルダの名前に使用できる文字列に変換

`create_system_name(name)`

ファイル名、及びフォルダ名に使用できない文字を使用可能な文字に置き換えた文字列を返します。

- name(str): ファイル名、フォルダ名に使用したい文字列です。

#### 外部ファイルからオブジェクトを読み込む

`load_object(file)`<br>
外部ファイルからオブジェクトを読み込みます。

この関数は[save_object](#%e5%a4%96%e9%83%a8%e3%83%95%e3%82%a1%e3%82%a4%e3%83%ab%e3%81%ab%e3%82%aa%e3%83%96%e3%82%b8%e3%82%a7%e3%82%af%e3%83%88%e3%82%92%e4%bf%9d%e5%ad%98%e3%81%99%e3%82%8b)で保存したオブジェクトの読み込みを想定しています。<br>

ファイルに保存されているオブジェクトは`単一`である必要があります。

複数のオブジェクトを扱いたい場合は、[pickle_dict](#pickle_dict)を使用してください。

- file(str or Path): 読み込むファイルです。

#### 外部ファイルにオブジェクトを保存する

`save_object(obj, file, protocol=4)`

オブジェクトを外部ファイルに保存します。

`pickle`で保存できないオブジェクトには未対応です。

読み込みには[load_object](#%e5%a4%96%e9%83%a8%e3%83%95%e3%82%a1%e3%82%a4%e3%83%ab%e3%81%8b%e3%82%89%e3%82%aa%e3%83%96%e3%82%b8%e3%82%a7%e3%82%af%e3%83%88%e3%82%92%e8%aa%ad%e3%81%bf%e8%be%bc%e3%82%80)の使用を想定しています。<br>

この関数で保存されるオブジェクトは`単一`です。

複数のオブジェクトを扱いたい場合は、[pickle_dict](#pickle_dict)を使用してください。

- obj(object): 保存したいオブジェクトです。
- file(str or Path): 書き出し先のファイルです。
- protocol(int): `pickle`で使用するプロトコルです。

#### リスト等から重複を取り除いたリストを生成する

`deduplicate(list_)`

リスト等から重複を除去します。

順番を保持するので、`set()`で順番を破壊したくない際に使用できます。
`type(list_) is str`の場合、文字列から重複が除去されてしまうので注意してください。

- list_(iter): 重複を除去したいオブジェクト。

#### リスト等から重複を取り除いて 1 行ずつ外部ファイルに書き出す

`deduplicate_file(file=None, *adds, show_result=False, strict=True)`

`txtファイル`から重複行と空行を取り除きます。

- file(str or Path): 対象のファイルです。
- adds(tuple): 渡したオブジェクトをそれぞれ`str()`してファイルの先頭に追加します。
- show_result(bool): 何行削除したか結果を表示します。
- strict(bool): 特定条件で例外を投げます。

    例外の発生条件
    - 引数`file`が`None`時に表示されるダイアログでファイルを選択しない、かつ、`strict=True`。
    - `file`が存在せず、かつ、`adds`に値が存在しない、かつ、`strict=True`。
    - `file`の拡張子が`.txt`以外、かつ、`strict=True`。

使い方

```Python
# テストファイル生成用関数
def create_testfile():
    lines = [1, 3, 3, 3, 5, 5, 5, 5, 5, 7, 7, 7, 7, 7, 7, 7, 9, 9, 9, 9, 9, 9, 9, 9, 9, 0, 2, 2, 4, 4, 4, 4, 6, 6, 6, 6, 6, 6, 8, 8, 8, 8, 8, 8, 8, 8]
    with open('test.txt', 'w') as f:
        f.write("\n".join(map(str, lines)))

# 存在するファイルから重複除去
create_testfile()
deduplicate_file('test.txt', show_result=True, strict=True)
"""
36行削除しました。
"""
# test.txtの中身は[1, 3, 5, 7, 9, 0, 2, 4, 6, 8]の改行区切り


# 存在するファイルに要素を追加して重複除去
create_testfile()
deduplicate_file('test.txt', *range(10), show_result=True, strict=True)
"""
46行削除しました。
"""
# test.txtの中身は[0, 1, 2, 3 , 4, 5, 6, 7, 8, 9]の改行区切り

# 存在しないファイルに要素を追加して除去
not_exists_file = 'test2.txt'
deduplicate_file(not_exists_file, *['odd' if x % 2 else x for x in range(10)], show_result=True, strict=True)
"""
4行削除しました。
"""
# test2.txtの中身は[0, odd, 2, 4, 6, 8]の改行区切り

# 存在しないファイルから重複除去
not_exists_file = 'test2.txt'
deduplicate_file(not_exists_file, show_result=True, strict=True)
"""
.
.
.
...
FileNotFoundError: test2.txtは存在しません。
"""
```

#### 質問を行い真偽値の回答を取得する

`confirm(message, use_gui=True, prompt='>')`

`はい`、`いいえ`で答えられるような質問を行ってユーザーからの回答を`bool値`として取得します。<br>

`use_gui`が有効の場合、質問を`tkinter.messagebox.askyesno`で行います。

無効の場合は標準出力で質問を行います。

また、その場合は`[yes, y, はい, ハイ, no, n, いいえ, イイエ]`以外の入力は受け取りません。

※大文字、小文字は区別されません。前後の空白は除去されます。<br>

- message(str): 質問文です。
- use_gui(bool): 質問を GUI で行うか、標準出力で行うかです。
- prompt (str): 標準出力で質問する時のプロンプト文字列です。

#### 入力を受け取り指定した型に変換する

`type_input(convert_type=str, message="", prompt='>', allow_empty=False)`

ユーザーからの入力を受け取り、指定した型に変換した値を返します。

変換が正常に行われる文字列を受け取るまで、この処理が継続されます。

変換可能な型は、`__call__`で文字列からの変換が定義されているものになります。

- convert_type(type): 変換する型です。
- message(str): ユーザーへの入力を促すメッセージです。
- prompt(str): ユーザーへの入力を促すメッセージの末尾です。
- allow_empty(bool): 空文字列を受け取った場合 None を返して終了するかです。

#### 辞書オブジェクトから例外を起こさずに値を取得する

`get_dict_in_value(dict_)`

辞書オブジェクトから例外を起こさずに値を取得する関数です。

初めに引数`dict_`を与えると`dict_`から値を取得するための`_(key)`関数を返します。

この関数は`__getitem__`が定義されているクラスであれば動作する場合があります。

- dict\_(dict): 辞書オブジェクトです。
- \_(function): 値取得用関数です。
  - key(str): 取得したいキーです。

使い方

```Python
# テスト用辞書
sample_dict = {'test1': 1, 'test2': 'test2', 'test3': 3.0}

# 読み込み用関数の取得
getter = get_dict_in_value(sample_dict)

# get_dict_in_value(sample_dict)の戻り値の型
getter_type = type(getter)

# 存在するキーの取得
get_exists_key = getter('test2')

# 存在しないキーの取得
get_not_exists_key = getter('test4')

# 変数の内容を出力
print(f'{sample_dict=}')
print(f'{getter_type=}')
print(f'{get_exists_key=}')
print(f'{get_not_exists_key=}')
"""
sample_dict={'test1': 1, 'test2': 'test2', 'test3': 3.0}
getter_type=<class 'function'>
get_exists_key='test2'
get_not_exists_key=None
"""
```

#### 標準出力で進捗表示など同じ行を使いまわす

`fline(text='', end=False)`

標準出力で同じ行を更新したい時などに使える関数です。

`text`にオブジェクトを渡すと`str(text)`してから出力されます。

`end`を`True`にすることで出力後に改行します。

```python
fline(1) # 直後の2に上書きされる。
fline(2, True)
fline(3)
"""
2
3
"""
```

## pickle_dict

### 概要

このモジュールでは`pickle`でのオブジェクト管理を`辞書オブジェクト風`に行えるようにする為の`PDict`クラスを定義しています。<br><br>

### 使い方

#### 管理オブジェクトの生成

`Pdict(file, reset_data=False)`

以降紹介する方法は、ここで紹介する方法のどちらかを実行してから行ってください。

オブジェクト生成時に`reset_data=True`を設定すると既存の管理ファイルを初期化してから開始します。

- file(str or Path): 管理ファイルです。
- reset_data(bool): 管理ファイルが既に存在する場合に初期化するかです。

```Python
# インポートします。
from otsutil.pickle_dict import PDict

# 利用するファイルを設定します。
file = 'pdata/ptest.bin'

# with文で生成(推奨)
with PDict(file) as p:
  # このブロックで以降紹介する処理を記述します。

# 変数に代入して生成
p = PDict(file)
# 以降紹介する処理を記述します。
p.close()  # ファイルの保守を行います。
```

#### 要素の追加・変更

追加には 2 つの方法があり、1 つのシンタックスシュガーがあります

##### add

`add(**kargs)`

追加専用メソッド。

このメソッドでは`未定義のキー`に要素を追加することができます。

複数キーを同時に定義することもできます。

既存のキーを指定した場合、警告を出力し、上書きは`行われません`。

- kargs: key=object。

```Python
# 要素の追加
p.add(test1='add')

# 複数要素の追加
p.add(test2=2, test3=3.0)

# 定義済みのキーに要素を追加しようとする
p.add(test1=1)

# 出力。
p.show_all()
"""
[key='test1']の追加に失敗しました。
既に存在するキーです。
このキーを上書きしたい場合は、[rewrite]メソッドを使用してください。
test1: add
test2: 2
test3: 3.0
"""
```

##### rewrite

`rewrite(key, value, *, allow_add)`

追加・変更可能メソッド。

このメソッドでは既存キーの値を上書きすることができます。

このメソッドでは既存キーにも影響を与えられる性質上、ヒューマンエラー対策で一つずつしか変更できません。

- key(str): 対象のキーです。
- value(object): 保存するオブジェクトです。
- allow_add(bool): 存在しないキーの追加を許可するかです。

```Python
p.rewrite('test2', '書き換え')
p.rewrite('test4', 'rewriteで追加')
p.show_all()
"""
test1: add
test2: 書き換え
test3: 3.0
test4: rewriteで追加
"""
```

##### 辞書風に追加

シンタックスシュガー。

内部的には`rewrite(key="test1", value=1, allow_add=True)`されています。

```Python
p['test1'] = '辞書風に書き換え'
p['test5'] = '辞書風に追加'
p.show_all()
"""
test1: 辞書風に書き換え
test2: 書き換え
test3: 3.0
test4: rewriteで追加
test5: 辞書風に追加
"""
```

#### 要素の削除

要素の削除は`del文`と`remove`メソッドで行えます。

##### remove

`remove(key)`

指定したキーを削除します。

キーを削除したあと管理ファイルの保守処理を呼び出します。<br>

存在しないキーを指定した場合何もしません。

- key(str): 削除するキーです。

```Python
p.remove('test1')
p.show_all()
"""
test2: 書き換え
test3: 3.0
test4: rewriteで追加
test5: 辞書風に追加
"""
```

##### del

シンタックスシュガー。

内部的には`remove(key='test4')`されています。

```Python
del p['test4']
p.show_all()
```

#### 一覧の取得・出力

##### キーと値の一覧の出力

`show_all()`

このメソッドでは保存しているオブジェクトの一覧を出力します。

`{key}: {value}`という形で 1 行ずつ出力します。

`{value}`は文字列として出力されるので型によっては意味の分からない出力になる可能性があります。

```Python
p.show_all()
"""
test2: 書き換え
test3: 3.0
test5: 辞書風に追加
"""
```

##### キー一覧の取得

`get_keys()`

`p.keys`でも取得することができますが、`pop()`や`del`など、リストに変更を加えると、管理オブジェクトに影響が出てしまうので、こちらを利用してください。

```Python
keys = p.get_keys()
print(f'{keys=}')
"""
keys=['test2', 'test3', 'test5']
"""
```

##### 値の一覧の取得

`values()`

一つのリストに全てのオブジェクトを格納して返すので、メモリを圧迫する可能性があります。

使用は推奨しません。

```Python
values = p.values()
print(f'{values=}')
"""
values=['書き換え', 3.0, '辞書風に追加']
"""
```

#### キーの存在確認

キーの存在確認には`has_key`か`in文`が使えます。

内部的には等価です。

```Python
# 'test1'の確認
has_test1 = p.has_key('test1')
in_test1 = 'test1' in p

# 'test2'の確認
has_test2 = p.has_key('test2')
in_test2 = 'test2' in p
"""
has_test1=False
in_test1=False
has_test2=True
in_test2=True
"""
```

#### 要素数の確認

`len(p)`

管理しているオブジェクトの数を取得できます。

```Python
p.show_all()
length = len(p)
print(f'{length=}')
"""
test2: 書き換え
test3: 3.0
test5: 辞書風に追加
length=3
"""
```

#### iter

`for文`では key を一つずつ取り出します。

```Python
for key in p:
  print(f'{key=}')
"""
key='test2'
key='test3'
key='test5'
"""
```

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
