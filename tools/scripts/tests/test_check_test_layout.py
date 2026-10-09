"""Tests for check_test_layout.py."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from check_test_layout import problems  # noqa: E402


class ProblemsTest(unittest.TestCase):
    def folder(self, root, files):
        tmp = Path(tempfile.mkdtemp()) / "integration"
        tmp.mkdir()
        (tmp / "main.rs").write_text(root)
        for name in files:
            (tmp / name).write_text("")
        return tmp

    def test_every_file_loaded(self):
        folder = self.folder(
            'mod a;\npub mod common;\n#[path = "b.rs"]\nmod b;\n',
            ["a.rs", "b.rs", "common.rs"],
        )
        self.assertEqual(problems(folder), [])

    def test_missing_file(self):
        folder = self.folder("mod a;\n", ["a.rs", "new.rs"])
        self.assertEqual(len(problems(folder)), 1)
        self.assertIn("new.rs is not loaded", problems(folder)[0])

    def test_mod_inside_a_block_counts(self):
        folder = self.folder("#[cfg(feature = \"pg\")]\n    mod a;\n", ["a.rs"])
        self.assertEqual(problems(folder), [])

    def test_files_in_subfolders_are_not_test_files(self):
        folder = self.folder("", [])
        (folder / "support").mkdir()
        (folder / "support" / "mod.rs").write_text("")
        self.assertEqual(problems(folder), [])


if __name__ == "__main__":
    unittest.main()
