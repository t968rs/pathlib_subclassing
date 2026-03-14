# Source - https://codereview.stackexchange.com/q/162426
# Posted by Carel, modified by community. See post 'Timeline' for change history
# Retrieved 2026-03-10, License - CC BY-SA 3.0

from pathlib import Path as _Path_, PosixPath as _PosixPath_, WindowsPath  as _WindowsPath_
import os
from dataclasses import dataclass
from typing import ClassVar, Optional


@dataclass(kw_only=True, frozen=True)
class PathChild:
    name: str
    file: bool = True
    relpath: Optional[_Path_] = None

    @classmethod
    def from_parent( cls, parent: _Path_, child: _Path_, file: Optional[bool] = None) -> "PathChild":
        if not child.is_relative_to(parent):
            raise ValueError(f"Child path {child} is not relative to parent path {parent}")

        relpath = child.relative_to(parent)

        if file is None:
            file = child.is_file()

        return cls(name=child.name, file=file, relpath=relpath)

class PathCN(_Path_) :
    # Cache of dynamically-created concrete classes for user subclasses.
    _concrete_classes: ClassVar[dict] = {}

    def __new__(cls, *args, **kvps):
        native_os_cls = _WindowsPath_ if os.name == 'nt' else _PosixPath_
        os_cls = WindowsPath if os.name == 'nt' else PosixPath

        if issubclass(cls, native_os_cls):
            # cls is already a concrete (OS-flavoured) class; use it directly.
            target_cls = cls
        elif cls is PathCN:
            # Plain PathCN() → use the OS-specific concrete class.
            target_cls = os_cls
        else:
            # User-defined subclass of PathCN: combine it with the OS-specific
            # class so that the result is an instance of the user's subclass AND
            # a proper OS path, while keeping __init__ callable.
            if cls not in PathCN._concrete_classes:
                PathCN._concrete_classes[cls] = type(cls.__name__, (cls, os_cls), {})
            target_cls = PathCN._concrete_classes[cls]

        return super().__new__(target_cls, *args, **kvps)

    def __init__(self, *args):
        super().__init__(*args)
        self._children: list[PathChild] = []

    def _process_path_item(self, path: _Path_) -> PathChild:
        """Internal helper: build a :class:`PathChild` for *path* relative to this path.

        Subclasses can override this method to customise how each discovered
        file is represented, without having to worry about which concrete
        ``Path`` flavour (Windows vs. Posix) they are running on.
        """
        return PathChild.from_parent(self, path, file=path.is_file())

    def walk_directory(self) -> list[PathChild]:
        """Recursively walk this directory and return a list of :class:`PathChild` objects.

        Every regular file found beneath this path is passed through
        :meth:`_process_path_item` and the results are stored in
        :attr:`children`.  Raises :class:`ValueError` when called on a
        non-directory path.
        """
        if not self.is_dir():
            raise ValueError(f"{self} is not a directory")

        self._children = [
            self._process_path_item(item)
            for item in self.rglob("*")
            if item.is_file()
        ]
        return list(self._children)

    @property
    def children(self) -> list[PathChild]:
        """Files discovered by the last call to :meth:`walk_directory`."""
        return list(self._children)


class WindowsPath(_WindowsPath_, PathCN) :
    pass

class PosixPath(_PosixPath_, PathCN) :
    pass
