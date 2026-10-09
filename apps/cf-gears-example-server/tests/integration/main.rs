//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Cargo builds this file as one test
//! target and does not build the files next to it on their own. A new test
//! file in this folder needs a `mod` line here; `tools/scripts/check_test_layout.py`
//! fails without one. Helpers that several files use are declared here once,
//! and the files `use crate::<helper>`.
#![allow(clippy::expect_used, clippy::unwrap_used)]

mod approvals_config;
mod cli_smoke_tests;
mod migrate_command_tests;
mod products_config;
// By path, so the `mod` lines inside it look in this folder, as they did when
// it was a crate root of its own.
#[path = "products_wiring.rs"]
mod products_wiring;
mod schema_guard_boot;
