//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.
#![cfg_attr(coverage_nightly, feature(coverage_attribute))]
#![allow(clippy::expect_used, clippy::unwrap_used)]

mod common;

#[path = "api_children_test.rs"]
mod api_children_test;
#[path = "api_conversions_test.rs"]
mod api_conversions_test;
#[path = "api_envelope_test.rs"]
mod api_envelope_test;
#[path = "api_metadata_test.rs"]
mod api_metadata_test;
#[path = "api_service_accounts_test.rs"]
mod api_service_accounts_test;
#[path = "api_status_mapping_test.rs"]
mod api_status_mapping_test;
#[path = "api_tenants_test.rs"]
mod api_tenants_test;
#[path = "api_users_test.rs"]
mod api_users_test;
#[path = "barrier_carve_out_integration.rs"]
mod barrier_carve_out_integration;
#[path = "client_service_accounts_test.rs"]
mod client_service_accounts_test;
#[path = "conversion_integration.rs"]
mod conversion_integration;
#[path = "conversion_integration_pg.rs"]
mod conversion_integration_pg;
#[path = "coord_lease_integration_pg.rs"]
mod coord_lease_integration_pg;
#[path = "integrity_integration.rs"]
mod integrity_integration;
#[path = "integrity_integration_pg.rs"]
mod integrity_integration_pg;
#[path = "lease_guard_sqlite.rs"]
mod lease_guard_sqlite;
#[path = "lease_manager_sqlite.rs"]
mod lease_manager_sqlite;
#[path = "lifecycle_edges_integration.rs"]
mod lifecycle_edges_integration;
#[path = "lifecycle_integration.rs"]
mod lifecycle_integration;
#[path = "list_children_integration.rs"]
mod list_children_integration;
#[path = "list_descendants_integration.rs"]
mod list_descendants_integration;
#[path = "list_descendants_integration_pg.rs"]
mod list_descendants_integration_pg;
#[path = "metadata_integration.rs"]
mod metadata_integration;
#[path = "metadata_integration_pg.rs"]
mod metadata_integration_pg;
#[path = "metadata_repo_integration.rs"]
mod metadata_repo_integration;
#[path = "migrations_test.rs"]
mod migrations_test;
#[path = "reads_integration.rs"]
mod reads_integration;
#[path = "repair_integration.rs"]
mod repair_integration;
#[path = "retention_integration.rs"]
mod retention_integration;
#[path = "updates_integration.rs"]
mod updates_integration;
