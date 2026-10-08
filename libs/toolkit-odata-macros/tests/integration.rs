//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.

#[path = "compile_tests.rs"]
mod compile_tests;
#[path = "expansion_demo.rs"]
mod expansion_demo;
#[path = "odata_schema.rs"]
mod odata_schema;
#[path = "ui.rs"]
mod ui;
