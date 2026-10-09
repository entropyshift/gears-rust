//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Cargo builds this file as one test
//! target and does not build the files next to it on their own. A new test
//! file in this folder needs a `mod` line here; `tools/scripts/check_test_layout.py`
//! fails without one. Helpers that several files use are declared here once,
//! and the files `use crate::<helper>`.
#![allow(clippy::expect_used, clippy::panic, clippy::unwrap_used)]

mod common;

mod catalog_integration_ch;
mod crypto_provider_required;
mod readiness_integration_ch;
mod records_ingest_integration_ch;
mod records_query_integration_ch;
