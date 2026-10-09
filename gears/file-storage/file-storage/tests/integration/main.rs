//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Cargo builds this file as one test
//! target and does not build the files next to it on their own. A new test
//! file in this folder needs a `mod` line here; `tools/scripts/check_test_layout.py`
//! fails without one. Helpers that several files use are declared here once,
//! and the files `use crate::<helper>`.
#![allow(clippy::doc_markdown, clippy::expect_used, clippy::unwrap_used)]

mod audit_test;
mod cleanup_test;
mod content_hash_modes_test;
mod enforce_test;
mod error_mapping_test;
mod finalize_test;
mod idempotency_authz_test;
mod list_authz_test;
mod migration_test;
mod multipart_test;
mod ownership_test;
mod policy_authz_test;
mod policy_test;
mod service_test;
mod usage_test;
mod version_repo_test;
