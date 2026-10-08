"""Tests for check_test_layout.py."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from check_test_layout import problems  # noqa: E402


class ProblemsTest(unittest.TestCase):
    def crate(self, manifest, root, files):
        tmp = Path(tempfile.mkdtemp())
        (tmp / "tests").mkdir()
        (tmp / "Cargo.toml").write_text(manifest)
        (tmp / "tests" / "integration.rs").write_text(root)
        for name in files:
            (tmp / "tests" / name).write_text("")
        return tmp

    def test_every_file_loaded(self):
        crate = self.crate(
            "[package]\nautotests = false\n",
            '#[path = "a.rs"]\nmod a;\nmod common;\n#[path = "b.rs"]\nmod b;\n',
            ["a.rs", "b.rs", "common.rs"],
        )
        self.assertEqual(problems(crate), [])

    def test_missing_file(self):
        crate = self.crate("[package]\nautotests = false\n", '#[path = "a.rs"]\nmod a;\n', ["a.rs", "new.rs"])
        self.assertEqual(len(problems(crate)), 1)
        self.assertIn("new.rs is not loaded", problems(crate)[0])

    def test_own_binary_declared_in_manifest(self):
        crate = self.crate(
            '[package]\nautotests = false\n\n[[test]]\nname = "own"\npath = "tests/own.rs"\n',
            '#[path = "a.rs"]\nmod a;\n',
            ["a.rs", "own.rs"],
        )
        self.assertEqual(problems(crate), [])

    def test_autotests_left_on(self):
        crate = self.crate("[package]\n", '#[path = "a.rs"]\nmod a;\n', ["a.rs"])
        self.assertEqual(len(problems(crate)), 1)
        self.assertIn("autotests = false", problems(crate)[0])

    def test_files_in_subfolders_are_not_test_files(self):
        crate = self.crate("[package]\nautotests = false\n", "", [])
        (crate / "tests" / "support").mkdir()
        (crate / "tests" / "support" / "mod.rs").write_text("")
        self.assertEqual(problems(crate), [])


if __name__ == "__main__":
    unittest.main()
