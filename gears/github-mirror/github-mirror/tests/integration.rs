//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.
#![allow(clippy::expect_used, clippy::unwrap_used)]

mod common;

#[path = "branches_endpoint_test.rs"]
mod branches_endpoint_test;
#[path = "cache_endpoint_test.rs"]
mod cache_endpoint_test;
#[path = "check_runs_endpoint_test.rs"]
mod check_runs_endpoint_test;
#[path = "comments_endpoint_test.rs"]
mod comments_endpoint_test;
#[path = "commit_comments_endpoint_test.rs"]
mod commit_comments_endpoint_test;
#[path = "commit_files_endpoint_test.rs"]
mod commit_files_endpoint_test;
#[path = "commit_statuses_endpoint_test.rs"]
mod commit_statuses_endpoint_test;
#[path = "commits_endpoint_test.rs"]
mod commits_endpoint_test;
#[path = "contributors_endpoint_test.rs"]
mod contributors_endpoint_test;
#[path = "deployments_endpoint_test.rs"]
mod deployments_endpoint_test;
#[path = "gear_lifecycle_test.rs"]
mod gear_lifecycle_test;
#[path = "github_client_test.rs"]
mod github_client_test;
#[path = "health_endpoint_test.rs"]
mod health_endpoint_test;
#[path = "http_cache_test.rs"]
mod http_cache_test;
#[path = "issue_events_endpoint_test.rs"]
mod issue_events_endpoint_test;
#[path = "issue_reactions_endpoint_test.rs"]
mod issue_reactions_endpoint_test;
#[path = "issue_timeline_endpoint_test.rs"]
mod issue_timeline_endpoint_test;
#[path = "issues_endpoint_test.rs"]
mod issues_endpoint_test;
#[path = "item_endpoints_test.rs"]
mod item_endpoints_test;
#[path = "labels_endpoint_test.rs"]
mod labels_endpoint_test;
#[path = "migrations_test.rs"]
mod migrations_test;
#[path = "milestones_endpoint_test.rs"]
mod milestones_endpoint_test;
#[path = "paged_listing_test.rs"]
mod paged_listing_test;
#[path = "pull_request_commits_endpoint_test.rs"]
mod pull_request_commits_endpoint_test;
#[path = "pull_request_files_endpoint_test.rs"]
mod pull_request_files_endpoint_test;
#[path = "pulls_endpoint_test.rs"]
mod pulls_endpoint_test;
#[path = "releases_endpoint_test.rs"]
mod releases_endpoint_test;
#[path = "repos_endpoint_test.rs"]
mod repos_endpoint_test;
#[path = "resume_test.rs"]
mod resume_test;
#[path = "review_comments_endpoint_test.rs"]
mod review_comments_endpoint_test;
#[path = "review_threads_endpoint_test.rs"]
mod review_threads_endpoint_test;
#[path = "reviews_endpoint_test.rs"]
mod reviews_endpoint_test;
#[path = "sdk_client_test.rs"]
mod sdk_client_test;
#[path = "storage_tenancy_test.rs"]
mod storage_tenancy_test;
#[path = "sweep_watermark_storage_test.rs"]
mod sweep_watermark_storage_test;
#[path = "sync_deadline_test.rs"]
mod sync_deadline_test;
#[path = "sync_endpoint_test.rs"]
mod sync_endpoint_test;
#[path = "sync_pool_test.rs"]
mod sync_pool_test;
#[path = "sync_sessions_endpoint_test.rs"]
mod sync_sessions_endpoint_test;
#[path = "sync_state_storage_test.rs"]
mod sync_state_storage_test;
#[path = "tags_endpoint_test.rs"]
mod tags_endpoint_test;
#[path = "user_endpoints_test.rs"]
mod user_endpoints_test;
#[path = "verification_test.rs"]
mod verification_test;
#[path = "workflow_jobs_endpoint_test.rs"]
mod workflow_jobs_endpoint_test;
#[path = "workflow_runs_endpoint_test.rs"]
mod workflow_runs_endpoint_test;
