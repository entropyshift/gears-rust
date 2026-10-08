//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.
#![cfg_attr(coverage_nightly, feature(coverage_attribute))]

mod common;

#[path = "advisory_locks_native.rs"]
mod advisory_locks_native;
#[path = "config_tests.rs"]
mod config_tests;
#[path = "db_generic.rs"]
mod db_generic;
#[path = "error_classification.rs"]
mod error_classification;
#[path = "group_scope_postgres.rs"]
mod group_scope_postgres;
#[path = "manager_tests.rs"]
mod manager_tests;
// `mod` is a keyword: tests/mod.rs (the pg and sqlite suites) loads as `suites`.
#[path = "odata_compile.rs"]
mod odata_compile;
#[path = "odata_null_like.rs"]
mod odata_null_like;
#[path = "options_tests.rs"]
mod options_tests;
#[path = "outbox_trace_completion_native.rs"]
mod outbox_trace_completion_native;
#[path = "params_integration.rs"]
mod params_integration;
#[path = "precedence_tests.rs"]
mod precedence_tests;
#[path = "retry_helper_sqlite.rs"]
mod retry_helper_sqlite;
#[path = "secure_insert_from_select_sqlite.rs"]
mod secure_insert_from_select_sqlite;
#[path = "secure_odata_sqlite.rs"]
mod secure_odata_sqlite;
#[path = "mod.rs"]
mod suites;
#[path = "ui.rs"]
mod ui;
