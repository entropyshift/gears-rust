//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.

#[path = "e2e_http2_test.rs"]
mod e2e_http2_test;
#[path = "e2e_smoke_test.rs"]
mod e2e_smoke_test;
#[path = "management_api_test.rs"]
mod management_api_test;
#[path = "proxy_integration.rs"]
mod proxy_integration;
#[path = "proxy_request_rejections.rs"]
mod proxy_request_rejections;
