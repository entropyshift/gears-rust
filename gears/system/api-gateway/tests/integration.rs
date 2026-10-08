//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.
#![allow(clippy::expect_used)]

#[path = "access_log_tests.rs"]
mod access_log_tests;
#[path = "auth_disabled_root_context.rs"]
mod auth_disabled_root_context;
#[path = "auth_middleware.rs"]
mod auth_middleware;
#[path = "body_limit_tests.rs"]
mod body_limit_tests;
#[path = "cors_tests.rs"]
mod cors_tests;
#[path = "health_endpoints.rs"]
mod health_endpoints;
#[path = "http_metrics_tests.rs"]
mod http_metrics_tests;
#[path = "integration_router.rs"]
mod integration_router;
#[path = "license_middleware.rs"]
mod license_middleware;
#[path = "middleware_order.rs"]
mod middleware_order;
#[path = "mime_validation_integration.rs"]
mod mime_validation_integration;
#[path = "request_id.rs"]
mod request_id;
#[path = "throttling_tests.rs"]
mod throttling_tests;
