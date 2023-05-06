import abc
import builtins
import shutil
from io import StringIO
from pathlib import Path
from typing import (
    Callable,
    TextIO,
)

from mock_open import MockOpen

from mljet.utils.types import PathLike


class IOMock(metaclass=abc.ABCMeta):
    """
    Mocks the filesystem for testing purposes.

    The filesystem is represented as a tree, where each node is a dict.
    The keys are the names of the files and directories, and the values
    are either dicts (for directories) or strings (for files).

    The tree is stored in the `tree` attribute, and the root of the tree
    is stored in the `start_point` attribute.

    The `to_forward` argument is a list of paths to files that will be
    copied to the mock filesystem. This is useful for testing code that
    reads from the filesystem.

    The `fs_tree` property returns a string representation of the tree.
    """

    def __init__(self, to_forward=None):
        self.tree = {}
        self.o_mocker = MockOpen()
        self.to_forward = to_forward or []

    def __enter__(self) -> "IOMock":
        """Enter to the mock context"""
        for entry in self.to_forward:
            with open(Path(entry), "r") as fi, self.o_mocker(
                Path(entry).resolve(), "w"
            ) as fo:
                fo.write(fi.read())
        self.mock()
        self.flush()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the mock context"""
        self.unmock()
        self.flush()

    def append(self, path: PathLike):
        """Append a file to the mocker."""
        tree = self.tree
        for entry in Path(path).parts:
            tree[entry] = tree.get(entry, {})
            tree = tree[entry]

    @abc.abstractmethod
    def mock(self):
        """Mock the IO."""
        raise NotImplementedError

    @abc.abstractmethod
    def unmock(self):
        """Unmock the IO."""
        raise NotImplementedError

    @property
    def start_point(self) -> dict:
        """The root of the tree, started
        from the most common ancestor."""
        tree = self.tree
        prev = None
        while len(tree) == 1:
            prev = tree
            tree, *_ = list(tree.values())
        return prev

    @property
    def fs_tree(self) -> str:
        """Return a string representation of the tree."""
        io = StringIO()
        print("|", file=io)

        def walk(tree, depth=0):
            for key, value in sorted(tree.items()):
                adder = "└── " if depth == 0 else "├── "
                prefix = "|" if depth > 0 else ""
                print(f"{prefix}{'    ' * depth}{adder}{key}", file=io)
                if isinstance(value, dict):
                    walk(value, depth + 1)

        walk(self.start_point)
        return io.getvalue()

    def flush(self):
        """Flush the tree."""
        last_filename = None
        for call in self.o_mocker.mock_calls:
            instruction = call[0]
            if instruction == "":
                last_filename = call.args[0]
            if "write" in instruction:
                self.append(last_filename)


class DefaultIOMock(IOMock):
    """Default IO mock."""

    def __init__(self, to_forward=None):
        super().__init__(to_forward)
        self.original_open = open
        self.original_pathlib_mkdirs = Path.mkdir
        self.original_pathlib_exists = Path.exists
        self.original_shutil_copyfile = shutil.copyfile

    def __enter__(self) -> "DefaultIOMock":
        """Enter to the mock context."""
        super().__enter__()
        return self

    def mock(self):
        """Mock the IO."""
        builtins.open = self.__repl_open
        Path.mkdir = self._make_pathlib_mkdirs()
        Path.exists = self._make_pathlib_exists()
        shutil.copyfile = self._make_shutil_copyfile()

    def unmock(self):
        """Unmock the IO."""
        builtins.open = self.original_open
        Path.mkdir = self.original_pathlib_mkdirs
        Path.exists = self.original_pathlib_exists
        shutil.copyfile = self.original_shutil_copyfile

    def _make_pathlib_mkdirs(self, *args, **kwargs) -> Callable:
        def __pathlib_mkdirs_mock(path, *args, **kwargs):
            self.flush()
            _path = Path(path).resolve()
            self.append(_path)

        return __pathlib_mkdirs_mock

    def _make_pathlib_exists(self, *args, **kwargs) -> Callable:
        def __pathlib_exists(path):
            self.flush()
            path = Path(path).resolve()
            stem = path.name
            tree = self.tree
            for entry in path.parts[:-1]:
                tree = tree.get(entry, {})
            return stem in tree

        return __pathlib_exists

    def _make_shutil_copyfile(self, *args, **kwargs) -> Callable:
        def __shutil_copyfile(src, dst):
            self.flush()
            with self.__repl_open(
                Path(src).resolve(), "rb"
            ) as fi, self.__repl_open(Path(src).resolve(), "wb") as fo:
                fo.write(fi.read())

        return __shutil_copyfile

    def __repl_open(self, path, mode="r", encoding=None, *kwargs) -> TextIO:
        return self.o_mocker(
            Path(path).resolve(), mode=mode, encoding=encoding, *kwargs
        )


def test_default_iomock():
    """Test the default IO mock."""
    mocker = DefaultIOMock()
    with mocker:
        with open("test.txt", "w") as fo:
            fo.write("Hello, world!")
        with open("test.txt", "r") as fi:
            assert fi.read() == "Hello, world!"
        with open("model.pkl", "wb") as fo:
            fo.write(b"Hello, world!")
        with open("model.pkl", "rb") as fi:
            assert fi.read() == b"Hello, world!"
        Path("a/b/c").mkdir(parents=True, exist_ok=True)
        assert Path("test.txt").exists()
        assert Path("model.pkl").exists()
    assert (
        mocker.fs_tree
        == """|
└── tests
|    ├── a
|        ├── b
|            ├── c
|    ├── model.pkl
|    ├── test.txt
"""
    )
