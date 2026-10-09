//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Cargo builds this file as one test
//! target and does not build the files next to it on their own. A new test
//! file in this folder needs a `mod` line here; `tools/scripts/check_test_layout.py`
//! fails without one. Helpers that several files use are declared here once,
//! and the files `use crate::<helper>`.
#![cfg_attr(coverage_nightly, feature(coverage_attribute))]
#![allow(clippy::unwrap_used)]

mod clients;
mod grpc_hostile_peer;
mod grpc_integration;
mod mock_manual;
mod mock_mockall;
mod multi_provide;
mod resolving_directory;
mod runtime_eventual_readiness;
mod telemetry;
mod v1_v2_coexistence;
