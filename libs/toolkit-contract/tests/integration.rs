//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.

#[path = "concurrency_limit.rs"]
mod concurrency_limit;
#[path = "consumer_wiring_concurrency.rs"]
mod consumer_wiring_concurrency;
#[path = "contract_error_derive.rs"]
mod contract_error_derive;
#[allow(dead_code)] // `pub` items were used as the root of their own binary
#[path = "grpc_client_platform_secctx.rs"]
mod grpc_client_platform_secctx;
#[path = "multipart_roundtrip.rs"]
mod multipart_roundtrip;
#[allow(dead_code)] // `pub` items were used as the root of their own binary
#[path = "otel_propagation.rs"]
mod otel_propagation;
#[path = "proto_bridge_derive.rs"]
mod proto_bridge_derive;
#[allow(dead_code)] // `pub` items were used as the root of their own binary
#[path = "rest_client_codegen.rs"]
mod rest_client_codegen;
#[allow(dead_code)] // `pub` items were used as the root of their own binary
#[path = "rest_client_platform_secctx.rs"]
mod rest_client_platform_secctx;
#[allow(dead_code)] // `pub` items were used as the root of their own binary
#[path = "rest_contract_macro.rs"]
mod rest_contract_macro;
#[allow(dead_code)] // `pub` items were used as the root of their own binary
#[path = "rest_server_codegen.rs"]
mod rest_server_codegen;
#[path = "wiring_config.rs"]
mod wiring_config;
