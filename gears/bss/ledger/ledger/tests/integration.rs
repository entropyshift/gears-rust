//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.

#[path = "metrics_emit.rs"]
mod metrics_emit;
#[path = "module_test.rs"]
mod module_test;
#[path = "postgres_allocate_fx.rs"]
mod postgres_allocate_fx;
#[path = "postgres_audit.rs"]
mod postgres_audit;
#[path = "postgres_balance_caches.rs"]
mod postgres_balance_caches;
#[path = "postgres_bola.rs"]
mod postgres_bola;
#[path = "postgres_chain.rs"]
mod postgres_chain;
#[path = "postgres_chargeback_concurrency.rs"]
mod postgres_chargeback_concurrency;
#[path = "postgres_chargeback_fx.rs"]
mod postgres_chargeback_fx;
#[path = "postgres_chargebacks.rs"]
mod postgres_chargebacks;
#[path = "postgres_credit.rs"]
mod postgres_credit;
#[path = "postgres_credit_concurrency.rs"]
mod postgres_credit_concurrency;
#[path = "postgres_credit_note.rs"]
mod postgres_credit_note;
#[path = "postgres_cross_tenant.rs"]
mod postgres_cross_tenant;
#[path = "postgres_debit_note.rs"]
mod postgres_debit_note;
#[path = "postgres_dual_control.rs"]
mod postgres_dual_control;
#[path = "postgres_entry_annotation.rs"]
mod postgres_entry_annotation;
#[path = "postgres_exception.rs"]
mod postgres_exception;
#[path = "postgres_executor.rs"]
mod postgres_executor;
#[path = "postgres_fx_revaluation_mode.rs"]
mod postgres_fx_revaluation_mode;
#[path = "postgres_idempotency.rs"]
mod postgres_idempotency;
#[path = "postgres_inquiry.rs"]
mod postgres_inquiry;
#[path = "postgres_invoice_post.rs"]
mod postgres_invoice_post;
#[path = "postgres_invoice_post_fx.rs"]
mod postgres_invoice_post_fx;
#[path = "postgres_journal.rs"]
mod postgres_journal;
#[path = "postgres_manual_adjustment.rs"]
mod postgres_manual_adjustment;
#[path = "postgres_migration_idempotency.rs"]
mod postgres_migration_idempotency;
#[path = "postgres_payer_state.rs"]
mod postgres_payer_state;
#[path = "postgres_payment_concurrency.rs"]
mod postgres_payment_concurrency;
#[path = "postgres_payment_returns.rs"]
mod postgres_payment_returns;
#[path = "postgres_payments.rs"]
mod postgres_payments;
#[path = "postgres_period_close.rs"]
mod postgres_period_close;
#[path = "postgres_period_guard.rs"]
mod postgres_period_guard;
#[path = "postgres_period_open.rs"]
mod postgres_period_open;
#[path = "postgres_pii.rs"]
mod postgres_pii;
#[path = "postgres_policy_version.rs"]
mod postgres_policy_version;
#[path = "postgres_posting.rs"]
mod postgres_posting;
#[path = "postgres_precedence_policy.rs"]
mod postgres_precedence_policy;
#[path = "postgres_projector.rs"]
mod postgres_projector;
#[path = "postgres_provisioning.rs"]
mod postgres_provisioning;
#[path = "postgres_queue.rs"]
mod postgres_queue;
#[path = "postgres_queue_concurrency.rs"]
mod postgres_queue_concurrency;
#[path = "postgres_read_surface.rs"]
mod postgres_read_surface;
#[path = "postgres_recognition_build.rs"]
mod postgres_recognition_build;
#[path = "postgres_recognition_change.rs"]
mod postgres_recognition_change;
#[path = "postgres_recognition_disaggregation.rs"]
mod postgres_recognition_disaggregation;
#[path = "postgres_recognition_run.rs"]
mod postgres_recognition_run;
#[path = "postgres_reconciliation.rs"]
mod postgres_reconciliation;
#[path = "postgres_reference.rs"]
mod postgres_reference;
#[path = "postgres_refund.rs"]
mod postgres_refund;
#[path = "postgres_refund_dispute_hold.rs"]
mod postgres_refund_dispute_hold;
#[path = "postgres_refund_fx.rs"]
mod postgres_refund_fx;
#[path = "postgres_retention.rs"]
mod postgres_retention;
#[path = "postgres_revaluation_fx.rs"]
mod postgres_revaluation_fx;
#[path = "postgres_scale_lock.rs"]
mod postgres_scale_lock;
#[path = "postgres_schema.rs"]
mod postgres_schema;
#[path = "postgres_settlement_return_fx.rs"]
mod postgres_settlement_return_fx;
#[path = "postgres_tieout.rs"]
mod postgres_tieout;
#[path = "rest_adjustments.rs"]
mod rest_adjustments;
#[path = "rest_audit.rs"]
mod rest_audit;
#[path = "rest_credit.rs"]
mod rest_credit;
#[path = "rest_disputes.rs"]
mod rest_disputes;
#[path = "rest_journal_entries.rs"]
mod rest_journal_entries;
#[path = "rest_payments.rs"]
mod rest_payments;
#[path = "rest_provisioning.rs"]
mod rest_provisioning;
#[path = "rest_recognition.rs"]
mod rest_recognition;
#[path = "rest_refunds.rs"]
mod rest_refunds;
#[path = "sqlite_adjustment_repo.rs"]
mod sqlite_adjustment_repo;
#[path = "sqlite_chain_state.rs"]
mod sqlite_chain_state;
#[path = "sqlite_debit_note_repo.rs"]
mod sqlite_debit_note_repo;
#[path = "sqlite_payment_refund_cap.rs"]
mod sqlite_payment_refund_cap;
#[path = "sqlite_reconciliation_lifecycle.rs"]
mod sqlite_reconciliation_lifecycle;
#[path = "sqlite_refund_repo.rs"]
mod sqlite_refund_repo;
#[path = "sqlite_repo.rs"]
mod sqlite_repo;
#[path = "sqlite_scale_resolver.rs"]
mod sqlite_scale_resolver;
