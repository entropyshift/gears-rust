//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.
#![allow(clippy::expect_used, clippy::unwrap_used)]

#[path = "detection_precedence_tests.rs"]
mod detection_precedence_tests;
#[path = "docx_parser_tests.rs"]
mod docx_parser_tests;
#[path = "image_parser_tests.rs"]
mod image_parser_tests;
#[path = "magika_detector_tests.rs"]
mod magika_detector_tests;
#[path = "magika_timeout_tests.rs"]
mod magika_timeout_tests;
#[path = "path_traversal_tests.rs"]
mod path_traversal_tests;
#[path = "pptx_parser_tests.rs"]
mod pptx_parser_tests;
#[path = "xlsx_parser_tests.rs"]
mod xlsx_parser_tests;
