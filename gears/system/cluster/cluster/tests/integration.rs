//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.

mod common;

#[path = "caller_ownership.rs"]
mod caller_ownership;
#[path = "conformance.rs"]
mod conformance;
#[path = "consumer_wiring.rs"]
mod consumer_wiring;
#[path = "coordination.rs"]
mod coordination;
#[path = "descriptor_seams.rs"]
mod descriptor_seams;
#[path = "election_subscription_status.rs"]
mod election_subscription_status;
#[path = "grpc_services.rs"]
mod grpc_services;
#[path = "mixed_backend_integration.rs"]
mod mixed_backend_integration;
#[path = "oop_bootstrap.rs"]
mod oop_bootstrap;
#[path = "oop_probe_ordering.rs"]
mod oop_probe_ordering;
#[path = "oversized_error_hop.rs"]
mod oversized_error_hop;
#[path = "platform_credential.rs"]
mod platform_credential;
#[path = "remote_backends.rs"]
mod remote_backends;
#[path = "resolution.rs"]
mod resolution;
