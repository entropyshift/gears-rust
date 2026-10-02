#!/usr/bin/env python3
"""Unit tests for trybuild_suites.py.

    python3 -m unittest discover -s tools/scripts/tests
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import trybuild_suites as ts  # noqa: E402


class TestTrybuildFns(unittest.TestCase):
    def test_finds_the_enclosing_fn(self):
        src = """
#[test]
fn plain() { assert!(true); }

#[cfg(not(coverage_nightly))]
#[test]
fn ui() {
    let t = trybuild::TestCases::new();
    t.compile_fail("tests/ui/*.rs");
}
"""
        self.assertEqual(ts.trybuild_fns(src), ["ui"])

    def test_imported_form(self):
        src = "use trybuild::TestCases;\n#[test]\nfn compile_fail() {\n    TestCases::new().pass(\"x\");\n}\n"
        self.assertEqual(ts.trybuild_fns(src), ["compile_fail"])

    def test_no_trybuild(self):
        self.assertEqual(ts.trybuild_fns("#[test]\nfn a() {}\n"), [])


def target(name, kind, src):
    return {"name": name, "kind": [kind], "src_path": str(src)}


class TestBinary(unittest.TestCase):
    ROOT = Path("/ws/pkg")
    TARGETS = [
        target("pkg", "lib", ROOT / "src/lib.rs"),
        target("ui", "test", ROOT / "tests/ui.rs"),
        target("producer", "test", ROOT / "tests/producer.rs"),
        target("big", "test", ROOT / "tests/big/main.rs"),
        target("custom", "test", ROOT / "checks/custom_entry.rs"),
    ]

    def test_binary_top_level_file(self):
        self.assertEqual(ts.test_binary(self.ROOT / "tests/ui.rs", self.TARGETS), "ui")

    def test_binary_nested_module(self):
        self.assertEqual(ts.test_binary(self.ROOT / "tests/producer/builder.rs", self.TARGETS), "producer")

    def test_binary_main_rs_dir(self):
        self.assertEqual(ts.test_binary(self.ROOT / "tests/big/cases.rs", self.TARGETS), "big")

    def test_binary_custom_path(self):
        self.assertEqual(ts.test_binary(self.ROOT / "checks/custom_entry.rs", self.TARGETS), "custom")

    def test_binary_lib_unit_test(self):
        self.assertEqual(ts.test_binary(self.ROOT / "src/deep/mod.rs", self.TARGETS), "")

    def test_binary_outside_targets(self):
        self.assertIsNone(ts.test_binary(self.ROOT / "build.rs", self.TARGETS))


class TestScan(unittest.TestCase):
    def make_ws(self, d: Path, heavy_fn="spawns_cargo"):
        pkg = d / "pkg"
        (pkg / "tests" / "producer").mkdir(parents=True)
        (pkg / "src").mkdir()
        (pkg / "Cargo.toml").write_text("[package]\nname = \"pkg\"\n", encoding="utf-8")
        (pkg / "src" / "lib.rs").write_text("pub fn f() {}\n", encoding="utf-8")
        (pkg / "tests" / "producer.rs").write_text("mod builder;\n#[test]\nfn fast() {}\n", encoding="utf-8")
        (pkg / "tests" / "producer" / "builder.rs").write_text(
            "#[test]\nfn compile_failures() {\n    let t = trybuild::TestCases::new();\n}\n", encoding="utf-8")
        (pkg / "tests" / "heavy.rs").write_text(f"#[test]\nfn {heavy_fn}() {{}}\n", encoding="utf-8")
        # A nested package is scanned as its own member, not as part of pkg.
        (pkg / "inner").mkdir()
        (pkg / "inner" / "Cargo.toml").write_text("[package]\nname = \"inner\"\n", encoding="utf-8")
        (pkg / "inner" / "t.rs").write_text("fn x() { trybuild::TestCases::new(); }\n", encoding="utf-8")
        excluded = d / "skipme"
        (excluded / "tests").mkdir(parents=True)
        (excluded / "tests" / "ui.rs").write_text("fn ui() { trybuild::TestCases::new(); }\n", encoding="utf-8")
        return {
            "workspace_members": ["pkg-id", "skip-id"],
            "packages": [
                {"id": "pkg-id", "name": "pkg", "manifest_path": str(pkg / "Cargo.toml"), "targets": [
                    target("pkg", "lib", pkg / "src/lib.rs"),
                    target("producer", "test", pkg / "tests/producer.rs"),
                    target("heavy", "test", pkg / "tests/heavy.rs"),
                ]},
                {"id": "skip-id", "name": "skipme", "manifest_path": str(excluded / "Cargo.toml"), "targets": [
                    target("ui", "test", excluded / "tests/ui.rs"),
                ]},
            ],
        }

    def test_scan_finds_trybuild_and_heavy(self):
        heavy = [("pkg", "heavy", "spawns_cargo")]
        with tempfile.TemporaryDirectory() as d:
            meta = self.make_ws(Path(d))
            self.assertEqual(
                ts.scan(meta, {"skipme"}, heavy),
                [("pkg", "heavy", "spawns_cargo"), ("pkg", "producer", "compile_failures")],
            )

    def test_missing_heavy_entry_fails(self):
        heavy = [("pkg", "heavy", "spawns_cargo")]
        with tempfile.TemporaryDirectory() as d:
            meta = self.make_ws(Path(d), heavy_fn="renamed")
            with self.assertRaises(LookupError):
                ts.scan(meta, set(), heavy)


class TestOutput(unittest.TestCase):
    TESTS = [("pkg", "producer", "compile_failures"), ("lib-only", "", "unit_case")]

    def test_filterset(self):
        self.assertEqual(
            ts.filterset(self.TESTS),
            "(binary_id(=pkg::producer) & test(/(^|::)compile_failures$/))"
            " | (binary_id(=lib-only) & test(/(^|::)unit_case$/))",
        )

    def test_target_args(self):
        self.assertEqual(ts.target_args(self.TESTS), ["--lib", "--test", "producer"])


if __name__ == "__main__":
    unittest.main()
