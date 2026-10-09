//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Cargo builds this file as one test
//! target and does not build the files next to it on their own. A new test
//! file in this folder needs a `mod` line here; `tools/scripts/check_test_layout.py`
//! fails without one. Helpers that several files use are declared here once,
//! and the files `use crate::<helper>`.

mod common;

mod api_rest_test;
mod authz_integration_test;
mod create_group_target_tenant_test;
mod db_behavior_audit_test;
mod domain_unit_test;
mod group_service_test;
mod membership_service_test;
mod pg_concurrency_test;
mod pg_smoke_test;
mod query_recorder_test;
mod read_service_test;
mod seeding_test;
mod tenant_filtering_db_test;
mod tenant_scoping_test;
mod type_service_test;
