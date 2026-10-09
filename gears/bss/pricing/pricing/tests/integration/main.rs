//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Cargo builds this file as one test
//! target and does not build the files next to it on their own. A new test
//! file in this folder needs a `mod` line here; `tools/scripts/check_test_layout.py`
//! fails without one. Helpers that several files use are declared here once,
//! and the files `use crate::<helper>`.
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

// By path, so the `mod` lines inside it look in this folder, as they did when
// it was a crate root of its own.
#[path = "acceptance_receipts.rs"]
mod acceptance_receipts;
mod actor_names;
mod approval_doors;
mod approval_kinds;
mod approvals_inbox_source;
mod authoring_doors;
mod book_archive;
mod book_identity;
mod book_reads;
mod book_side;
mod book_writes;
mod broker_producer;
mod conditional_reads;
mod contract;
mod dimension_values;
mod entry_doors;
mod entry_model_migration;
mod entry_paging;
mod entry_usage;
// By path, so the `mod` lines inside it look in this folder, as they did when
// it was a crate root of its own.
#[path = "fulfilment_holds.rs"]
mod fulfilment_holds;
mod golden;
mod in_process_registry;
mod migration_chain;
mod module_test;
mod pg_harness;
mod plan_checks_batch;
mod plan_clone;
mod plan_codes;
mod plan_doors;
mod plan_item_doors;
mod plan_item_references;
mod plan_items_legacy;
mod plan_overview;
mod plan_repositories;
mod plan_revision_approvals;
mod plan_scheduled;
mod plan_summary;
mod policy_reshape_pending_units;
mod postgres_approvals;
mod postgres_book_archive;
mod postgres_book_reads;
mod postgres_book_writes;
mod postgres_commercial_receipts;
mod postgres_contract;
mod postgres_effective_policy;
mod postgres_entry_model_migration;
mod postgres_entry_paging;
mod postgres_indexes;
mod postgres_plan_summary;
mod postgres_plans;
mod postgres_policy_references_sku;
mod postgres_price_cancel_end;
mod postgres_pricing_seams;
mod postgres_references;
mod postgres_repositories;
mod postgres_revision_scheduled_migration;
mod postgres_schema_dump;
mod postgres_schema_guard;
mod postgres_settings_migration;
mod postgres_unit_submit_note_migration;
mod price_cancel_end_doors;
mod price_doors;
mod prices_subject;
mod pricing_events;
mod pricing_read_sdk;
mod pricing_seam_contract;
mod pure_model;
mod read_contract;
mod reference_machine;
mod reference_registry;
mod reference_ticker;
mod repositories;
mod response_enums;
mod rest_authz;
mod revision_reads;
mod revision_scheduled_migration;
mod schema_guard;
mod sellability;
mod served_contract;
mod settings_doors;
mod settings_migration;
mod skeleton_contract;
mod sku_reads;
mod sku_usage_scopes;
// By path, so the `mod` lines inside it look in this folder, as they did when
// it was a crate root of its own.
#[path = "sqlite_pricing_seams.rs"]
mod sqlite_pricing_seams;
mod sqlite_schema_dump;
mod stored_instant_census;
mod temporary_dates;
mod unit_submit_note_migration;
mod usage_rating_policy;
