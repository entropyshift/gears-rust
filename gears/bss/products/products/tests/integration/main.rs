//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Cargo builds this file as one test
//! target and does not build the files next to it on their own. A new test
//! file in this folder needs a `mod` line here; `tools/scripts/check_test_layout.py`
//! fails without one. Helpers that several files use are declared here once,
//! and the files `use crate::<helper>`.

mod guard_support;
mod pg_support;

mod audit_lifecycle_migration;
mod book_archive_e2e;
mod derived_meter_e2e;
mod pg_harness;
mod postgres_approvals_inbox;
mod postgres_archive;
mod postgres_audit_lifecycle_migration;
mod postgres_category_default;
mod postgres_derived_sku_unit;
mod postgres_derived_usage_type;
mod postgres_retired_default_migration;
mod postgres_schema_guard;
mod postgres_sku_category_migration;
mod postgres_sku_chain;
mod postgres_sku_lifecycle_honesty;
mod postgres_sku_list;
mod postgres_unit_submit_note_migration;
mod retired_default_migration;
mod schema_guard;
mod sku_category_migration;
mod stored_instant_census;
mod unit_submit_note_migration;
