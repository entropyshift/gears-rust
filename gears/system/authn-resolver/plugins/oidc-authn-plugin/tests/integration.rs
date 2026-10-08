//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.
#![allow(clippy::expect_used, clippy::panic)]

mod common;

#[path = "claim_mapper_integration.rs"]
mod claim_mapper_integration;
#[path = "clienthub_registration_integration.rs"]
mod clienthub_registration_integration;
#[path = "oidc_infra_integration.rs"]
mod oidc_infra_integration;
#[path = "s2s_exchange_integration.rs"]
mod s2s_exchange_integration;
