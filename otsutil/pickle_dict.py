import pickle
from pathlib import Path
from otsutil.exceptions import SetPathError


class PDict:
    """pickleでのオブジェクト保存を辞書風に扱えるようにするクラスです。

    Raises:
        SetPathError: 指定したファイルが不正な場合に投げられます。
        KeyError: loadで投げられます。
        ValueError: loadsで投げられます。
    """
    def __enter__(self):
        return self

    def __exit__(self, *ex):
        self.update()

    def __init__(self, file, *, reset_data=False):
        """オブジェクト管理の準備行います。

        Args:
            file (str or Path): 管理ファイル。
            reset_data (bool, optional): 既存のファイルをリセットして開始します。 初期値では追記になります。
        """
        self.__keys = []
        self._setup(file, reset_data)

    def __getitem__(self, item):
        """添え字に対応するオブジェクトを返します。

        このメソッドはload(item)と等価です。

        Args:
            item (str): キー。

        Returns:
            object: キーに対応するオブジェクト。
        """
        return self.load(item)

    def __setitem__(self, key, value):
        """添え字に対応するオブジェクトを保存します。

        このメソッドはrewrite(key, value)と等価です。

        Args:
            key (str): 添え字。
            value (object): オブジェクト。
        """
        self.rewrite(key, value)

    def _setup(self, file, reset_data):
        """初期化処理を行います。

        Args:
            file (str or Path): 管理ファイル。
            reset_data (bool): 既存の管理ファイルを初期化するか。
        """
        self._setup_file(file)
        self._setup_keys(reset_data)

    def _setup_file(self, file):
        """管理ファイルの確認と初期化処理を行います。

        Args:
            file (str or Path): 管理ファイル。

        Raises:
            SetPathError: 管理ファイルが何らかの理由で使用不能な場合に投げられます。
        """
        err = None
        self.__file = Path(file)
        self.__base_dir = Path(self.file.parent)
        if self.file.is_dir():
            err = f"{self.file.absolute()}はファイルではありません。"
        elif not self.file.exists():
            try:
                err = f"フォルダ[{self.base_dir.absolute()}]は使用できません。"
                self.base_dir.mkdir(parents=True, exist_ok=True)
                err = f"ファイル[{self.file.absolute()}]は使用できません。"
                self.file.touch()
                err = None
            except Exception:
                pass
        if err is not None:
            raise SetPathError(err)

    def _setup_keys(self, reset_data):
        """既存の管理ファイルからキー群を追加します。

        reset_data=Trueの場合、管理ファイルを削除して終了します。

        Args:
            reset_data (bool): 既存の管理ファイルを初期化するか。
        """
        if reset_data:
            self.file.unlink()
            return
        try:
            keys = []
            for dict_ in self._generate_reader():
                for key in dict_:
                    keys.append(key)
            self.__keys = keys
        except Exception:
            print("ファイルの読み込みに失敗しました。")
            keys = []
        self.update()

    def update(self):
        """管理ファイルの更新を行います。
        """
        tmp = self.base_dir / 'tmp.tmp'
        with open(tmp, 'wb') as f:
            for dict_ in self._generate_reader():
                for key in dict_:
                    if self.exists(key):
                        pickle.dump(dict_, f)
        with open(tmp, 'rb') as tf, open(self.file, 'wb') as file:
            file.write(tf.read())
        tmp.unlink()

    def _generate_reader(self):
        """管理ファイルからオブジェクトを一つずつ読み込みます。

        返るオブジェクトは、{key: value}形式のdictです。

        Yields:
            dict: {key: value}。
        """
        file = self.file
        if not file.exists():
            return
        with open(file, 'rb') as f:
            while True:
                try:
                    yield pickle.load(f)
                except EOFError:
                    break

    def add(self, **kargs):
        """オブジェクトを管理ファイルに保存します。

        既に存在するキーを指定した場合、登録に失敗しますが例外は発生しません。

        例: add(key1=value1, key2=value2)
            管理ファイルに{key1: value1}, {key2: value2}という具合に書き出されます。

        """
        for key in kargs:
            if self.exists(key):
                err = (
                    f"[{key=}]の追加に失敗しました。",
                    "既に存在するキーです。",
                    "このキーを上書きしたい場合は、[rewrite]メソッドを使用してください。",
                )
                print("\n".join(err))
                continue
            try:
                with open(self.file, 'ab') as f:
                    pickle.dump({key: kargs[key]}, f)
                self.keys.append(key)
            except Exception as e:
                err = f"[{key=}]の追加に失敗しました。\n{e}"
                print(err)

    def rewrite(self, key, value, *, allow_add=True):
        """キーに保存するオブジェクトをvalueで上書きします。

        addと違い、単一のオブジェクトしか同時に扱うことができません。
        これは上書きできる性質上起こりえる、意図せぬデータを破壊してしまうヒューマンエラー対策です。

        Args:
            key (str): 書き換えるキー。
            value (object): 書き換え後の値。
            allow_add (bool, optional): 追加を許可するか。 Falseにすると存在しないキーをrewriteしても何も起こりません。
        """
        if self.exists(key) or allow_add:
            self.remove(key)
            data = {key: value}
            self.add(**data)

    def remove(self, key):
        """指定したキーの値を管理ファイルから削除します。

        存在しないキーを指定しても、最終的にキーが存在しなければいいので例外は投げられません。

        Args:
            key (str): キー。
        """
        if self.exists(key):
            index = self.keys.index(key)
            del self.keys[index]
            self.update()

    def load(self, key, *, strict=True):
        """指定したキーの値を返します。

        Args:
            key (str): キー。
            strict (bool, optional): 厳格モード。 Falseにすると、存在しないキーが指定されたとき、例外を投げる代わりにNoneを返します。

        Raises:
            KeyError: 厳格モード時に存在しないキーを指定すると投げられます。

        Returns:
            object: オブジェクト。
        """
        if self.exists(key):
            for dict_ in self._generate_reader():
                if key in dict_:
                    return dict_[key]
        err = f"[{key=}]の読み込みに失敗しました。"
        if strict:
            raise KeyError(err)
        else:
            print(err)
            return None

    def loads(self, *keys, strict=True):
        """指定したキー群に対応するオブジェクト群を返します。

        返るオブジェクトの要素数が単一であってもtuple[object]として返ります。
        オブジェクトの格納順序はキー群と対応します。

        Args:
            strict (bool, optional): 厳格モード。 キー群に存在しないキーが含まれるとき、例外が投げられます。

        Raises:
            ValueError: 厳格モード時に存在しないキーを指定すると投げられます。

        Returns:
            tuple[object]: キーに対応するオブジェクトが格納されたリスト。
        """
        err = None
        if not keys:
            err = "キーを一つ以上指定してください。"
        elif len(keys) != len(set(keys)):
            err = f"同じキーを重複して指定することはできません。"
        elif strict:
            if not all([self.exists(x) for x in keys]):
                err = f"[{keys=}]の中に存在しないキーが含まれています。"
        if err is not None:
            raise ValueError(err)
        objects = {x: None for x in range(len(keys))}
        for dict_ in self._generate_reader():
            for key in dict_:
                if key in keys:
                    index = keys.index(key)
                    objects[index] = dict_[key]
        return tuple(x[1] for x in sorted(objects.items(), key=lambda x: x[0]))

    def exists(self, key):
        """キーが存在するか確認します。

        Args:
            key (str): キー。

        Returns:
            bool: キーが存在するか。
        """
        return key in self.keys

    def show_keys(self):
        """現在管理しているキーの一覧を出力します。
        """
        for key in sorted(self.keys):
            print(key)

    def show_all(self):
        """現在管理しているキーと値の一覧を出力します。
        """
        outputs = []
        for dict_ in self._generate_reader():
            for key in dict_:
                outputs.append(f'{key}: {dict_[key]}')
        for line in sorted(outputs):
            print(line)

    @property
    def file(self):
        """管理ファイルのPathオブジェクトです。

        Returns:
            Path: 管理ファイルのPath。
        """
        return self.__file

    @property
    def base_dir(self):
        """管理ファイルの保存ディレクトリのPathです。

        Returns:
            Path: 管理ファイルの保存ディレクトリのPath。
        """
        return self.__base_dir

    @property
    def keys(self):
        """管理しているキー群です。

        Returns:
            list: キー群。
        """
        return self.__keys
