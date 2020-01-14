class InvalidStringError(Exception):
    """引数の文字列が無効な場合に投げられます。
    """
    pass


class NotSelectedError(Exception):
    """ファイル、または、フォルダ選択ダイアログでキャンセルされた場合に投げられます。
    """
    pass


class SetPathError(Exception):
    """ファイルまたは、ディレクトリのPathが使用できない場合に投げられます。
    """
    pass
