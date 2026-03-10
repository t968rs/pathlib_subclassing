# Source - https://codereview.stackexchange.com/q/162426
# Posted by Carel, modified by community. See post 'Timeline' for change history
# Retrieved 2026-03-10, License - CC BY-SA 3.0

from pathlib import Path as _Path_, PosixPath as _PosixPath_, WindowsPath  as _WindowsPath_
import os

class Path(_Path_) :
    def __new__(cls, *args, **kvps):
        print("Path*")
        return super().__new__(WindowsPath if os.name == 'nt' else PosixPath, *args, **kvps)

class WindowsPath(_WindowsPath_, Path) :
    pass

class PosixPath(_PosixPath_, Path) :
    pass
