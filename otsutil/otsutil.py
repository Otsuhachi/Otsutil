import base64
import pickle
from pathlib import Path


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
        file (str or pathlib.Path): 外部ファイル。

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
        file (str or pathlib.Path): 外部ファイル。
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
        file (str or pathlib.Path): 外部ファイル。
    """
    file = Path(file)
    tmp = []
    if not list_:
        return
    if file.exists():
        with open(file, 'r') as f:
            for line in f:
                tmp.append(line.strip())
    else:
        file.parent.mkdir(parents=True, exist_ok=True)
    tmp += [str(x) for x in list_]
    set_list = list(set(tmp))
    set_list.sort(key=tmp.index)
    text = "\n".join(set_list)
    with open(file, 'w') as f:
        f.write(text)


if __name__ == '__main__':
    print('This script is not main.')
