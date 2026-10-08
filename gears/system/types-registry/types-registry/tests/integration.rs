//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.
#![recursion_limit = "256"]

mod common;

#[path = "abstract_type_backends_test.rs"]
mod abstract_type_backends_test;
#[path = "admission_view_test.rs"]
mod admission_view_test;
#[path = "admission_worker_test.rs"]
mod admission_worker_test;
#[path = "api_rest_test.rs"]
mod api_rest_test;
#[path = "baseline_precondition_backends_test.rs"]
mod baseline_precondition_backends_test;
#[path = "compat_backends_test.rs"]
mod compat_backends_test;
#[path = "compat_test.rs"]
mod compat_test;
#[path = "config_test.rs"]
mod config_test;
#[path = "deletion_backends_test.rs"]
mod deletion_backends_test;
#[path = "deletion_key_test.rs"]
mod deletion_key_test;
#[path = "deletion_test.rs"]
mod deletion_test;
#[path = "dependency_repo_test.rs"]
mod dependency_repo_test;
#[path = "dependency_test.rs"]
mod dependency_test;
#[path = "discovery_filter_backends_test.rs"]
mod discovery_filter_backends_test;
#[path = "discovery_pattern_backends_test.rs"]
mod discovery_pattern_backends_test;
#[path = "dry_run_batch_backends_test.rs"]
mod dry_run_batch_backends_test;
#[path = "dry_run_batch_test.rs"]
mod dry_run_batch_test;
#[path = "dry_run_parity_test.rs"]
mod dry_run_parity_test;
#[path = "dry_run_test.rs"]
mod dry_run_test;
#[path = "edge_cases_tests.rs"]
mod edge_cases_tests;
#[path = "entity_test.rs"]
mod entity_test;
#[path = "family_test.rs"]
mod family_test;
#[path = "gts_012_semantics_tests.rs"]
mod gts_012_semantics_tests;
#[path = "gts_store_test.rs"]
mod gts_store_test;
#[path = "instance_test.rs"]
mod instance_test;
#[path = "migration_backends_test.rs"]
mod migration_backends_test;
#[path = "migration_test.rs"]
mod migration_test;
#[path = "missing_dependencies_test.rs"]
mod missing_dependencies_test;
#[path = "observability_test.rs"]
mod observability_test;
#[path = "operation_idempotency_test.rs"]
mod operation_idempotency_test;
#[path = "outbox_backends_test.rs"]
mod outbox_backends_test;
#[path = "outbox_test.rs"]
mod outbox_test;
#[path = "partial_admission_backends_test.rs"]
mod partial_admission_backends_test;
#[path = "partial_admission_test.rs"]
mod partial_admission_test;
#[path = "projected_read_backends_test.rs"]
mod projected_read_backends_test;
#[path = "quarantine_test.rs"]
mod quarantine_test;
#[path = "query_tests.rs"]
mod query_tests;
#[path = "ready_mode_tests.rs"]
mod ready_mode_tests;
#[path = "refresh_test.rs"]
mod refresh_test;
#[path = "registration_tests.rs"]
mod registration_tests;
#[path = "repo_backends_test.rs"]
mod repo_backends_test;
#[path = "repo_test.rs"]
mod repo_test;
#[path = "restart_persistence_test.rs"]
mod restart_persistence_test;
#[path = "revalidation_test.rs"]
mod revalidation_test;
#[path = "revision_race_backends_test.rs"]
mod revision_race_backends_test;
#[path = "revision_test.rs"]
mod revision_test;
#[path = "rg_gts_type_system_tests.rs"]
mod rg_gts_type_system_tests;
#[path = "schema_projection_test.rs"]
mod schema_projection_test;
#[path = "type_instance_tests.rs"]
mod type_instance_tests;
#[path = "validator_test.rs"]
mod validator_test;
