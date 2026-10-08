//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.
#![allow(clippy::doc_markdown, clippy::expect_used, clippy::unwrap_used)]

#[path = "audit_test.rs"]
mod audit_test;
#[path = "cleanup_test.rs"]
mod cleanup_test;
#[path = "content_hash_modes_test.rs"]
mod content_hash_modes_test;
#[path = "enforce_test.rs"]
mod enforce_test;
#[path = "error_mapping_test.rs"]
mod error_mapping_test;
#[path = "finalize_test.rs"]
mod finalize_test;
#[path = "idempotency_authz_test.rs"]
mod idempotency_authz_test;
#[path = "list_authz_test.rs"]
mod list_authz_test;
#[path = "migration_test.rs"]
mod migration_test;
#[path = "multipart_test.rs"]
mod multipart_test;
#[path = "ownership_test.rs"]
mod ownership_test;
#[path = "policy_authz_test.rs"]
mod policy_authz_test;
#[path = "policy_test.rs"]
mod policy_test;
#[path = "service_test.rs"]
mod service_test;
#[path = "usage_test.rs"]
mod usage_test;
#[path = "version_repo_test.rs"]
mod version_repo_test;
