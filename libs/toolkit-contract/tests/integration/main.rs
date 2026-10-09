//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Cargo builds this file as one test
//! target and does not build the files next to it on their own. A new test
//! file in this folder needs a `mod` line here; `tools/scripts/check_test_layout.py`
//! fails without one. Helpers that several files use are declared here once,
//! and the files `use crate::<helper>`.

mod concurrency_limit;
mod consumer_wiring_concurrency;
mod contract_error_derive;
#[allow(dead_code)] // `pub` items were used as the root of their own binary
mod grpc_client_platform_secctx;
mod multipart_roundtrip;
#[allow(dead_code)] // `pub` items were used as the root of their own binary
mod otel_propagation;
mod proto_bridge_derive;
#[allow(dead_code)] // `pub` items were used as the root of their own binary
mod rest_client_codegen;
#[allow(dead_code)] // `pub` items were used as the root of their own binary
mod rest_client_platform_secctx;
#[allow(dead_code)] // `pub` items were used as the root of their own binary
mod rest_contract_macro;
#[allow(dead_code)] // `pub` items were used as the root of their own binary
mod rest_server_codegen;
mod wiring_config;
