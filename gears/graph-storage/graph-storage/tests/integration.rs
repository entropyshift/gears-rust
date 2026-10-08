//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.
#![allow(clippy::expect_used, clippy::unwrap_used)]

#[allow(dead_code)]
mod conformance;
mod support;

#[path = "embedding_contract.rs"]
mod embedding_contract;
#[path = "fake_conformance.rs"]
mod fake_conformance;
#[path = "perf.rs"]
mod perf;
#[path = "pg_conformance.rs"]
mod pg_conformance;
#[path = "rest.rs"]
mod rest;
#[path = "service.rs"]
mod service;
