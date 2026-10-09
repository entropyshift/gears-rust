//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Cargo builds this file as one test
//! target and does not build the files next to it on their own. A new test
//! file in this folder needs a `mod` line here; `tools/scripts/check_test_layout.py`
//! fails without one. Helpers that several files use are declared here once,
//! and the files `use crate::<helper>`.
#![recursion_limit = "256"]

mod common;

mod abstract_type_backends_test;
mod admission_view_test;
mod admission_worker_test;
mod api_rest_test;
mod baseline_precondition_backends_test;
mod compat_backends_test;
mod compat_test;
mod config_test;
mod deletion_backends_test;
mod deletion_key_test;
mod deletion_test;
mod dependency_repo_test;
mod dependency_test;
mod discovery_filter_backends_test;
mod discovery_pattern_backends_test;
mod dry_run_batch_backends_test;
mod dry_run_batch_test;
mod dry_run_parity_test;
mod dry_run_test;
mod edge_cases_tests;
mod entity_test;
mod family_test;
mod gts_012_semantics_tests;
mod gts_store_test;
mod instance_test;
mod migration_backends_test;
mod migration_test;
mod missing_dependencies_test;
mod observability_test;
mod operation_idempotency_test;
mod outbox_backends_test;
mod outbox_test;
mod partial_admission_backends_test;
mod partial_admission_test;
mod projected_read_backends_test;
mod quarantine_test;
mod query_tests;
mod ready_mode_tests;
// By path, so the `mod` lines inside it look in this folder, as they did when
// it was a crate root of its own.
#[path = "refresh_test.rs"]
mod refresh_test;
mod registration_tests;
mod repo_backends_test;
mod repo_test;
mod restart_persistence_test;
mod revalidation_test;
mod revision_race_backends_test;
mod revision_test;
mod rg_gts_type_system_tests;
mod schema_projection_test;
mod type_instance_tests;
mod validator_test;
