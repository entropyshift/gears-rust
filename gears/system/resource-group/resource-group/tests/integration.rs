//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.

mod common;

#[path = "api_rest_test.rs"]
mod api_rest_test;
#[path = "authz_integration_test.rs"]
mod authz_integration_test;
#[path = "create_group_target_tenant_test.rs"]
mod create_group_target_tenant_test;
#[path = "db_behavior_audit_test.rs"]
mod db_behavior_audit_test;
#[path = "domain_unit_test.rs"]
mod domain_unit_test;
#[path = "group_service_test.rs"]
mod group_service_test;
#[path = "membership_service_test.rs"]
mod membership_service_test;
#[path = "pg_concurrency_test.rs"]
mod pg_concurrency_test;
#[path = "pg_smoke_test.rs"]
mod pg_smoke_test;
#[path = "query_recorder_test.rs"]
mod query_recorder_test;
#[path = "read_service_test.rs"]
mod read_service_test;
#[path = "seeding_test.rs"]
mod seeding_test;
#[path = "tenant_filtering_db_test.rs"]
mod tenant_filtering_db_test;
#[path = "tenant_scoping_test.rs"]
mod tenant_scoping_test;
#[path = "type_service_test.rs"]
mod type_service_test;
