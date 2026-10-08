//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.
#![allow(clippy::expect_used, clippy::too_many_lines, clippy::unwrap_used)]

mod common;

#[path = "consumer_group_rebalance_integration_tests.rs"]
mod consumer_group_rebalance_integration_tests;
#[path = "standalone_integration_tests.rs"]
mod standalone_integration_tests;
