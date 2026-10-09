//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Cargo builds this file as one test
//! target and does not build the files next to it on their own. A new test
//! file in this folder needs a `mod` line here; `tools/scripts/check_test_layout.py`
//! fails without one. Helpers that several files use are declared here once,
//! and the files `use crate::<helper>`.

mod common;

mod caller_ownership;
mod conformance;
mod coordination;
mod descriptor_seams;
mod election_subscription_status;
mod grpc_services;
mod mixed_backend_integration;
mod oop_bootstrap;
mod oversized_error_hop;
mod platform_credential;
mod remote_backends;
mod resolution;
