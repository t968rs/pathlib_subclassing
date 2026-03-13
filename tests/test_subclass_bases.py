"""Tests evaluating the usability of PathCN and PathChild."""
import tempfile
import unittest
from pathlib import Path

from path_def.subclass_bases import PathChild, PathCN


class TestPathChildFromParent(unittest.TestCase):
    """Usability tests for PathChild.from_parent."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)
        self.file = self.root / "hello.txt"
        self.file.write_text("hello")

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_basic_child(self):
        child = PathChild.from_parent(self.root, self.file)
        self.assertEqual(child.name, "hello.txt")
        self.assertTrue(child.file)
        self.assertEqual(child.relpath, Path("hello.txt"))

    def test_nested_child(self):
        subdir = self.root / "sub"
        subdir.mkdir()
        nested = subdir / "nested.txt"
        nested.write_text("nested")
        child = PathChild.from_parent(self.root, nested)
        self.assertEqual(child.name, "nested.txt")
        self.assertEqual(child.relpath, Path("sub/nested.txt"))

    def test_explicit_file_flag(self):
        child = PathChild.from_parent(self.root, self.file, file=False)
        self.assertFalse(child.file)

    def test_not_relative_raises(self):
        other = Path("/not/related/file.txt")
        with self.assertRaises(ValueError):
            PathChild.from_parent(self.root, other)

    def test_frozen_dataclass(self):
        child = PathChild.from_parent(self.root, self.file)
        with self.assertRaises(Exception):
            child.name = "changed"  # type: ignore[misc]


class TestPathCNInstantiation(unittest.TestCase):
    """Verify that PathCN can be instantiated and is a Path subclass."""

    def test_is_path_subclass(self):
        p = PathCN(".")
        self.assertIsInstance(p, Path)
        self.assertIsInstance(p, PathCN)

    def test_instantiate_from_string(self):
        p = PathCN("/tmp")
        self.assertEqual(p, Path("/tmp"))

    def test_instantiate_from_path(self):
        p = PathCN(Path("/tmp"))
        self.assertEqual(p, Path("/tmp"))

    def test_children_empty_before_walk(self):
        p = PathCN(".")
        self.assertEqual(p.children, [])


class TestPathCNWalkDirectory(unittest.TestCase):
    """Evaluate walk_directory usability."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)
        # Flat files
        (self.root / "a.txt").write_text("a")
        (self.root / "b.txt").write_text("b")
        # Nested file
        sub = self.root / "subdir"
        sub.mkdir()
        (sub / "c.txt").write_text("c")

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_returns_list_of_path_children(self):
        p = PathCN(self.root)
        children = p.walk_directory()
        self.assertIsInstance(children, list)
        self.assertTrue(all(isinstance(c, PathChild) for c in children))

    def test_all_files_found(self):
        p = PathCN(self.root)
        children = p.walk_directory()
        names = {c.name for c in children}
        self.assertEqual(names, {"a.txt", "b.txt", "c.txt"})

    def test_children_property_matches_walk(self):
        p = PathCN(self.root)
        returned = p.walk_directory()
        self.assertEqual(returned, p.children)

    def test_children_property_is_copy(self):
        """Mutating the returned list must not affect the internal state."""
        p = PathCN(self.root)
        p.walk_directory()
        copy = p.children
        copy.clear()
        self.assertEqual(len(p.children), 3)

    def test_nested_relpath(self):
        p = PathCN(self.root)
        children = p.walk_directory()
        nested = next(c for c in children if c.name == "c.txt")
        self.assertEqual(nested.relpath, Path("subdir/c.txt"))

    def test_walk_on_file_raises(self):
        file_path = self.root / "a.txt"
        p = PathCN(file_path)
        with self.assertRaises(ValueError):
            p.walk_directory()

    def test_walk_updates_children(self):
        """A second walk (after adding a file) updates children correctly."""
        p = PathCN(self.root)
        p.walk_directory()
        self.assertEqual(len(p.children), 3)

        (self.root / "d.txt").write_text("d")
        p.walk_directory()
        self.assertEqual(len(p.children), 4)


class TestPathCNSubclassing(unittest.TestCase):
    """Verify that _process_path_item can be overridden in subclasses."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)
        (self.root / "sample.txt").write_text("data")

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_override_process_path_item(self):
        """Subclasses can override _process_path_item without touching walk logic."""

        class UpperNamePath(PathCN):
            def _process_path_item(self, path):
                child = super()._process_path_item(path)
                # Return a new PathChild with the name uppercased
                return PathChild(name=child.name.upper(), file=child.file, relpath=child.relpath)

        p = UpperNamePath(self.root)
        children = p.walk_directory()
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0].name, "SAMPLE.TXT")


if __name__ == "__main__":
    unittest.main()
