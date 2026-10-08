//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.
#![allow(clippy::expect_used, clippy::panic, clippy::unwrap_used)]

mod common;

#[path = "catalog_integration_ch.rs"]
mod catalog_integration_ch;
#[path = "crypto_provider_required.rs"]
mod crypto_provider_required;
#[path = "readiness_integration_ch.rs"]
mod readiness_integration_ch;
#[path = "records_ingest_integration_ch.rs"]
mod records_ingest_integration_ch;
#[path = "records_query_integration_ch.rs"]
mod records_query_integration_ch;
