//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.

#[path = "axum_integration.rs"]
mod axum_integration;
#[path = "context.rs"]
mod context;
#[path = "error.rs"]
mod error;
#[path = "problem.rs"]
mod problem;
#[path = "resource_error_macro.rs"]
mod resource_error_macro;
#[path = "showcase.rs"]
mod showcase;
#[path = "ui.rs"]
mod ui;
#[path = "utoipa_integration.rs"]
mod utoipa_integration;
