class NotSelectedError(Exception):
    """ファイル、または、フォルダ選択ダイアログでキャンセルされた場合に投げられます。
    """
    pass


class SetPathError(Exception):
    """ファイルまたは、ディレクトリのPathが使用できない場合に投げられます。
    """
    pass
