//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.
#![allow(clippy::expect_used, clippy::unwrap_used)]

mod acceptance_support;
mod book_support;
#[path = "common/census.rs"]
mod census;
mod commercial_support;
#[macro_use]
mod contract_support;
mod entry_paging_support;
mod entry_support;
mod guard_support;
mod pg_support;
mod plan_support;
// Was a submodule of entry_support, under its allow(dead_code).
#[allow(dead_code)]
mod policy_support;
mod rest_support;
mod scheduled_support;
mod schema_dump;
mod seam_parity_support;
mod seam_support;
mod storage_support;

#[path = "acceptance_receipts.rs"]
mod acceptance_receipts;
#[path = "actor_names.rs"]
mod actor_names;
#[path = "approval_doors.rs"]
mod approval_doors;
#[path = "approval_kinds.rs"]
mod approval_kinds;
#[path = "approvals_inbox_source.rs"]
mod approvals_inbox_source;
#[path = "authoring_doors.rs"]
mod authoring_doors;
#[path = "book_archive.rs"]
mod book_archive;
#[path = "book_identity.rs"]
mod book_identity;
#[path = "book_reads.rs"]
mod book_reads;
#[path = "book_side.rs"]
mod book_side;
#[path = "book_writes.rs"]
mod book_writes;
#[path = "broker_producer.rs"]
mod broker_producer;
#[path = "conditional_reads.rs"]
mod conditional_reads;
#[path = "contract.rs"]
mod contract;
#[path = "dimension_values.rs"]
mod dimension_values;
#[path = "entry_doors.rs"]
mod entry_doors;
#[path = "entry_model_migration.rs"]
mod entry_model_migration;
#[path = "entry_paging.rs"]
mod entry_paging;
#[path = "entry_usage.rs"]
mod entry_usage;
#[path = "fulfilment_holds.rs"]
mod fulfilment_holds;
#[path = "golden.rs"]
mod golden;
#[path = "in_process_registry.rs"]
mod in_process_registry;
#[path = "migration_chain.rs"]
mod migration_chain;
#[path = "module_test.rs"]
mod module_test;
#[path = "pg_harness.rs"]
mod pg_harness;
#[path = "plan_checks_batch.rs"]
mod plan_checks_batch;
#[path = "plan_clone.rs"]
mod plan_clone;
#[path = "plan_codes.rs"]
mod plan_codes;
#[path = "plan_doors.rs"]
mod plan_doors;
#[path = "plan_item_doors.rs"]
mod plan_item_doors;
#[path = "plan_item_references.rs"]
mod plan_item_references;
#[path = "plan_items_legacy.rs"]
mod plan_items_legacy;
#[path = "plan_overview.rs"]
mod plan_overview;
#[path = "plan_repositories.rs"]
mod plan_repositories;
#[path = "plan_revision_approvals.rs"]
mod plan_revision_approvals;
#[path = "plan_scheduled.rs"]
mod plan_scheduled;
#[path = "plan_summary.rs"]
mod plan_summary;
#[path = "policy_reshape_pending_units.rs"]
mod policy_reshape_pending_units;
#[path = "postgres_approvals.rs"]
mod postgres_approvals;
#[path = "postgres_book_archive.rs"]
mod postgres_book_archive;
#[path = "postgres_book_reads.rs"]
mod postgres_book_reads;
#[path = "postgres_book_writes.rs"]
mod postgres_book_writes;
#[path = "postgres_commercial_receipts.rs"]
mod postgres_commercial_receipts;
#[path = "postgres_contract.rs"]
mod postgres_contract;
#[path = "postgres_effective_policy.rs"]
mod postgres_effective_policy;
#[path = "postgres_entry_model_migration.rs"]
mod postgres_entry_model_migration;
#[path = "postgres_entry_paging.rs"]
mod postgres_entry_paging;
#[path = "postgres_indexes.rs"]
mod postgres_indexes;
#[path = "postgres_plan_summary.rs"]
mod postgres_plan_summary;
#[path = "postgres_plans.rs"]
mod postgres_plans;
#[path = "postgres_policy_references_sku.rs"]
mod postgres_policy_references_sku;
#[path = "postgres_price_cancel_end.rs"]
mod postgres_price_cancel_end;
#[path = "postgres_pricing_seams.rs"]
mod postgres_pricing_seams;
#[path = "postgres_references.rs"]
mod postgres_references;
#[path = "postgres_repositories.rs"]
mod postgres_repositories;
#[path = "postgres_revision_scheduled_migration.rs"]
mod postgres_revision_scheduled_migration;
#[path = "postgres_schema_dump.rs"]
mod postgres_schema_dump;
#[path = "postgres_schema_guard.rs"]
mod postgres_schema_guard;
#[path = "postgres_settings_migration.rs"]
mod postgres_settings_migration;
#[path = "postgres_unit_submit_note_migration.rs"]
mod postgres_unit_submit_note_migration;
#[path = "price_cancel_end_doors.rs"]
mod price_cancel_end_doors;
#[path = "price_doors.rs"]
mod price_doors;
#[path = "prices_subject.rs"]
mod prices_subject;
#[path = "pricing_events.rs"]
mod pricing_events;
#[path = "pricing_read_sdk.rs"]
mod pricing_read_sdk;
#[path = "pricing_seam_contract.rs"]
mod pricing_seam_contract;
#[path = "pure_model.rs"]
mod pure_model;
#[path = "read_contract.rs"]
mod read_contract;
#[path = "reference_machine.rs"]
mod reference_machine;
#[path = "reference_registry.rs"]
mod reference_registry;
#[path = "reference_ticker.rs"]
mod reference_ticker;
#[path = "repositories.rs"]
mod repositories;
#[path = "response_enums.rs"]
mod response_enums;
#[path = "rest_authz.rs"]
mod rest_authz;
#[path = "revision_reads.rs"]
mod revision_reads;
#[path = "revision_scheduled_migration.rs"]
mod revision_scheduled_migration;
#[path = "schema_guard.rs"]
mod schema_guard;
#[path = "sellability.rs"]
mod sellability;
#[path = "served_contract.rs"]
mod served_contract;
#[path = "settings_doors.rs"]
mod settings_doors;
#[path = "settings_migration.rs"]
mod settings_migration;
#[path = "skeleton_contract.rs"]
mod skeleton_contract;
#[path = "sku_reads.rs"]
mod sku_reads;
#[path = "sku_usage_scopes.rs"]
mod sku_usage_scopes;
#[path = "sqlite_pricing_seams.rs"]
mod sqlite_pricing_seams;
#[path = "sqlite_schema_dump.rs"]
mod sqlite_schema_dump;
#[path = "stored_instant_census.rs"]
mod stored_instant_census;
#[path = "temporary_dates.rs"]
mod temporary_dates;
#[path = "unit_submit_note_migration.rs"]
mod unit_submit_note_migration;
#[path = "usage_rating_policy.rs"]
mod usage_rating_policy;
