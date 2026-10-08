//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.
#![allow(clippy::expect_used, clippy::unwrap_used)]

mod common;

#[path = "cache_integration.rs"]
mod cache_integration;
#[path = "conformance.rs"]
mod conformance;
#[path = "lifecycle_integration.rs"]
mod lifecycle_integration;
#[path = "lock_integration.rs"]
mod lock_integration;
#[path = "redis_specific.rs"]
mod redis_specific;
#[path = "watch_integration.rs"]
mod watch_integration;
