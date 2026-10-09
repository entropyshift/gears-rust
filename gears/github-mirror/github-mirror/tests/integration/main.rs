//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Cargo builds this file as one test
//! target and does not build the files next to it on their own. A new test
//! file in this folder needs a `mod` line here; `tools/scripts/check_test_layout.py`
//! fails without one. Helpers that several files use are declared here once,
//! and the files `use crate::<helper>`.
#![allow(clippy::expect_used, clippy::unwrap_used)]

mod common;

mod branches_endpoint_test;
mod cache_endpoint_test;
mod check_runs_endpoint_test;
mod comments_endpoint_test;
mod commit_comments_endpoint_test;
mod commit_files_endpoint_test;
mod commit_statuses_endpoint_test;
mod commits_endpoint_test;
mod contributors_endpoint_test;
mod deployments_endpoint_test;
mod gear_lifecycle_test;
mod github_client_test;
mod health_endpoint_test;
mod http_cache_test;
mod issue_events_endpoint_test;
mod issue_reactions_endpoint_test;
mod issue_timeline_endpoint_test;
mod issues_endpoint_test;
mod item_endpoints_test;
mod labels_endpoint_test;
mod migrations_test;
mod milestones_endpoint_test;
mod paged_listing_test;
mod pull_request_commits_endpoint_test;
mod pull_request_files_endpoint_test;
mod pulls_endpoint_test;
mod releases_endpoint_test;
mod repos_endpoint_test;
mod resume_test;
mod review_comments_endpoint_test;
mod review_threads_endpoint_test;
mod reviews_endpoint_test;
mod sdk_client_test;
mod storage_tenancy_test;
mod sweep_watermark_storage_test;
mod sync_deadline_test;
mod sync_endpoint_test;
mod sync_pool_test;
mod sync_sessions_endpoint_test;
mod sync_state_storage_test;
mod tags_endpoint_test;
mod user_endpoints_test;
mod verification_test;
mod workflow_jobs_endpoint_test;
mod workflow_runs_endpoint_test;
