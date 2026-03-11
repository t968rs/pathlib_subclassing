# Source - https://codereview.stackexchange.com/q/162426
# Posted by Carel, modified by community. See post 'Timeline' for change history
# Retrieved 2026-03-10, License - CC BY-SA 3.0

from pathlib import Path as _Path_, PosixPath as _PosixPath_, WindowsPath  as _WindowsPath_
import os
from dataclasses import dataclass
from typing import Optional


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
    def __new__(cls, *args, **kvps):
        print("Path*")
        return super().__new__(WindowsPath if os.name == 'nt' else PosixPath, *args, **kvps)

    # TODO add internal method that can be used by the subclasses to call super() without worrying about the correct parent class
    # TODO add public method, which calls a module-level function that will walk-down the input path (if it's a directory)
    #  and call the internal method for each file,
    #  so that the subclasses can easily implement functionality for directories without worrying about the correct parent class,
    # also populating a "children" attribute,

class WindowsPath(_WindowsPath_, PathCN) :
    pass

class PosixPath(_PosixPath_, PathCN) :
    pass
