//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.
#![cfg_attr(coverage_nightly, feature(coverage_attribute))]
#![allow(clippy::unwrap_used)]

#[path = "clients.rs"]
mod clients;
#[path = "grpc_hostile_peer.rs"]
mod grpc_hostile_peer;
#[path = "grpc_integration.rs"]
mod grpc_integration;
#[path = "mock_manual.rs"]
mod mock_manual;
#[path = "mock_mockall.rs"]
mod mock_mockall;
#[path = "multi_provide.rs"]
mod multi_provide;
#[path = "resolving_directory.rs"]
mod resolving_directory;
#[path = "runtime_eventual_readiness.rs"]
mod runtime_eventual_readiness;
#[path = "telemetry.rs"]
mod telemetry;
#[path = "v1_v2_coexistence.rs"]
mod v1_v2_coexistence;
