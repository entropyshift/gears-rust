//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.
#![allow(clippy::expect_used, clippy::unwrap_used)]

#[path = "domain_tests.rs"]
mod domain_tests;
#[path = "error_tests.rs"]
mod error_tests;
#[path = "service_tests.rs"]
mod service_tests;
#[path = "storage_tests.rs"]
mod storage_tests;
