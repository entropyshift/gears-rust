//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.

mod guard_support;
mod pg_support;

#[path = "audit_lifecycle_migration.rs"]
mod audit_lifecycle_migration;
#[path = "book_archive_e2e.rs"]
mod book_archive_e2e;
#[path = "derived_meter_e2e.rs"]
mod derived_meter_e2e;
#[path = "pg_harness.rs"]
mod pg_harness;
#[path = "postgres_approvals_inbox.rs"]
mod postgres_approvals_inbox;
#[path = "postgres_archive.rs"]
mod postgres_archive;
#[path = "postgres_audit_lifecycle_migration.rs"]
mod postgres_audit_lifecycle_migration;
#[path = "postgres_category_default.rs"]
mod postgres_category_default;
#[path = "postgres_derived_sku_unit.rs"]
mod postgres_derived_sku_unit;
#[path = "postgres_derived_usage_type.rs"]
mod postgres_derived_usage_type;
#[path = "postgres_retired_default_migration.rs"]
mod postgres_retired_default_migration;
#[path = "postgres_schema_guard.rs"]
mod postgres_schema_guard;
#[path = "postgres_sku_category_migration.rs"]
mod postgres_sku_category_migration;
#[path = "postgres_sku_chain.rs"]
mod postgres_sku_chain;
#[path = "postgres_sku_lifecycle_honesty.rs"]
mod postgres_sku_lifecycle_honesty;
#[path = "postgres_sku_list.rs"]
mod postgres_sku_list;
#[path = "postgres_unit_submit_note_migration.rs"]
mod postgres_unit_submit_note_migration;
#[path = "retired_default_migration.rs"]
mod retired_default_migration;
#[path = "schema_guard.rs"]
mod schema_guard;
#[path = "sku_category_migration.rs"]
mod sku_category_migration;
#[path = "stored_instant_census.rs"]
mod stored_instant_census;
#[path = "unit_submit_note_migration.rs"]
mod unit_submit_note_migration;
