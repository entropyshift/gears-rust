//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Cargo builds this file as one test
//! target and does not build the files next to it on their own. A new test
//! file in this folder needs a `mod` line here; `tools/scripts/check_test_layout.py`
//! fails without one. Helpers that several files use are declared here once,
//! and the files `use crate::<helper>`.
#![cfg_attr(coverage_nightly, feature(coverage_attribute))]

mod common;

mod advisory_locks_native;
mod config_tests;
mod db_generic;
mod error_classification;
mod group_scope_postgres;
mod manager_tests;
mod odata_compile;
mod odata_null_like;
mod options_tests;
mod outbox_trace_completion_native;
mod params_integration;
mod precedence_tests;
mod retry_helper_sqlite;
mod secure_insert_from_select_sqlite;
mod secure_odata_sqlite;
// `mod` is a keyword: mod.rs (the pg and sqlite suites) loads by path as `suites`.
#[path = "mod.rs"]
mod suites;
mod ui;
