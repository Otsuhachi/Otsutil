import base64
import pickle
import tkinter
from tkinter.filedialog import askdirectory, askopenfilename, askopenfilenames
from tkinter.messagebox import askyesno
from pathlib import Path
from otsutil.exceptions import NotSelectedError


def create_system_name(name):
    """引数の文字列からファイルシステムに使用できる文字列を返します。

    Args:
        name (str): ファイルシステムに使いたい文字列。

    Returns:
        str: ファイルシステムに使える文字列。
    """
    new_name = name
    old_words = (
        '\\',
        '/',
        ':',
        '*',
        '?',
        '"',
        '<',
        '>',
        '|',
    )
    new_words = (
        '-',
        '-',
        '：',
        '・',
        '？',
        "'",
        '＜',
        '＞',
        '｜',
    )
    for words in zip(old_words, new_words):
        old, new = words
        new_name = new_name.replace(old, new)
    return new_name


def load_object(file):
    """外部ファイルから暗号化されたオブジェクトを読み込みます。

    Args:
        file (str or Path): 外部ファイル。

    Raises:
        FileNotFoundError: 指定した外部ファイルが存在しない場合に投げられます。

    Returns:
        object: オブジェクト
    """
    file = Path(file)
    if not file.exists():
        raise FileNotFoundError
    with open(file, 'r') as f:
        b64_str = f.read().encode()
    str_to_byte = base64.b64decode(b64_str)
    return pickle.loads(str_to_byte)


def save_object(obj, file, protocol=4):
    """オブジェクトを暗号化して外部ファイルに保存します。

    Args:
        obj (object): オブジェクト。
        file (str or Path): 外部ファイル。
        protocol (int, optional): pickleのprotocol。`1-5`まで選択可能。 指定しなければ `4`。
    """
    file = Path(file)
    obj_to_byte = pickle.dumps(obj, protocol=4)
    byte_to_str = base64.b64encode(obj_to_byte).decode('utf-8')
    if not file.exists():
        file.parent.mkdir(parents=True, exist_ok=True)
    with open(file, 'w') as f:
        f.write(byte_to_str)


def write_set_lines(list_, file):
    """リストの要素を外部ファイルに一行ずつ書き出します。

    主に重複して知らせる必要のないログ等を出力する際に使います。
    既に外部ファイルが存在している場合は、既存の出力を取り込んでから重複を取り除きます。

    人に見やすい形で出力することを目的としているので、文字列以外の要素をリストに含めることは推奨されません。

    Args:
        list_ (list): リスト。
        file (str or Path): 外部ファイル。
    """
    file = Path(file)
    tmp = []
    if not list_:
        return
    if file.exists():
        with open(file, 'r') as f:
            tmp += [y for x in f if (y:=x.strip())]
    else:
        file.parent.mkdir(parents=True, exist_ok=True)
    tmp += [y for x in list_ if (y:=str(x).strip())]
    set_list = list(set(tmp))
    set_list.sort(key=tmp.index)
    text = "\n".join(set_list)
    with open(file, 'w') as f:
        f.write(text)


def choice_file(*types, title=None, multi=False, strict=True):
    """ファイルを選択するダイアログを表示し、選択されたファイルのPathオブジェクト、または、list[Path]オブジェクトを返します。

    Args:
        title (str, optional): 設定するとダイアログのタイトルになります。
        multi (bool, optional): Trueにすると、複数ファイルを選択可能になります。初期値はFalse。
        strict (bool, optional): Falseにすると、選択がキャンセルされた場合にNoneを返します。

    Raises:
        NotSelectedError: `strict=True`かつ、選択がキャンセルされた場合。

    Returns:
        Path or list[Path] or None: 選択したファイルのパスです。
    """
    root = tkinter.Tk()
    root.withdraw()
    if types:
        file_type = [(f'{x}ファイル', f'*.{x}') for x in types if x]
    else:
        file_type = [("", "*")]
    script_dir = Path()
    option = {'filetypes': file_type, 'initialdir': script_dir}
    if title is not None:
        option['title'] = title
    if multi:
        file = [Path(x) for x in askopenfilenames(**option)]
    else:
        file = Path(askopenfilename(**option))
    if file in (Path(), []):
        if strict:
            err = f'{file=}'
            raise NotSelectedError(err)
        return None
    return file


def choice_dir(title=None):
    """ディレクトリを選択するダイアログを表示し、選択されたディレクトリのPathオブジェクトを返します。

    Args:
        title (str, optional): 設定するとダイアログのタイトルになります。

    Returns:
        Path: ディレクトリパス。
    """
    option = {}
    if title is not None:
        option['title'] = title
    root = tkinter.Tk()
    root.withdraw()
    script_dir = Path()
    option['initialdir'] = script_dir
    dir = askdirectory(**option)
    return Path(dir)


def confirm(message, use_gui=True, prompt='>'):
    """[yes], [no]で回答できる質問を行い、その結果を真偽値にして返します。

    Args:
        message (str): 質問文です。
        use_gui (bool, optional): 有効にするとtkinterにようGUIで質問を行い、無効にすると標準出力で質問を行います。
        prompt (str, optional): 標準出力で質問を行う際のプロンプト文字列です。

    Returns:
        bool: ユーザーからの回答。
    """
    while True:
        if use_gui:
            root = tkinter.Tk()
            root.withdraw()
            return askyesno('確認', message)
        else:
            answer = input(f'{message}{prompt}').strip().lower()
            if answer in ('yes', 'y', 'はい', 'ハイ'):
                return True
            elif answer in ('no', 'n', 'いいえ', 'イイエ'):
                return
        print('回答は以下のいずれかを入力してください。')
        print('yes: yes, y, はい, ハイ')
        print('no: no, n, いいえ, イイエ')
