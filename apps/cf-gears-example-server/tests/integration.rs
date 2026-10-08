//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.
#![allow(clippy::expect_used, clippy::unwrap_used)]

#[path = "approvals_config.rs"]
mod approvals_config;
#[path = "cli_smoke_tests.rs"]
mod cli_smoke_tests;
#[path = "migrate_command_tests.rs"]
mod migrate_command_tests;
#[path = "products_config.rs"]
mod products_config;
#[path = "products_wiring.rs"]
mod products_wiring;
#[path = "schema_guard_boot.rs"]
mod schema_guard_boot;
