//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Cargo builds this file as one test
//! target and does not build the files next to it on their own. A new test
//! file in this folder needs a `mod` line here; `tools/scripts/check_test_layout.py`
//! fails without one. Helpers that several files use are declared here once,
//! and the files `use crate::<helper>`.
#![cfg_attr(coverage_nightly, feature(coverage_attribute))]
#![allow(clippy::expect_used, clippy::unwrap_used)]

mod common;

mod api_children_test;
mod api_conversions_test;
mod api_envelope_test;
mod api_metadata_test;
mod api_service_accounts_test;
mod api_status_mapping_test;
mod api_tenants_test;
mod api_users_test;
mod barrier_carve_out_integration;
mod client_service_accounts_test;
mod conversion_integration;
mod conversion_integration_pg;
mod coord_lease_integration_pg;
mod integrity_integration;
mod integrity_integration_pg;
mod lease_guard_sqlite;
mod lease_manager_sqlite;
mod lifecycle_edges_integration;
mod lifecycle_integration;
mod list_children_integration;
mod list_descendants_integration;
mod list_descendants_integration_pg;
mod metadata_integration;
mod metadata_integration_pg;
mod metadata_repo_integration;
mod migrations_test;
mod reads_integration;
mod repair_integration;
mod retention_integration;
mod updates_integration;
