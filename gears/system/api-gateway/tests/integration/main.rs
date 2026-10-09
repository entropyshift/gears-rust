//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Cargo builds this file as one test
//! target and does not build the files next to it on their own. A new test
//! file in this folder needs a `mod` line here; `tools/scripts/check_test_layout.py`
//! fails without one. Helpers that several files use are declared here once,
//! and the files `use crate::<helper>`.
#![allow(clippy::expect_used)]

mod access_log_tests;
mod auth_disabled_root_context;
mod auth_middleware;
mod body_limit_tests;
mod cors_tests;
mod health_endpoints;
mod http_metrics_tests;
mod integration_router;
mod license_middleware;
mod middleware_order;
mod mime_validation_integration;
mod request_id;
mod throttling_tests;
