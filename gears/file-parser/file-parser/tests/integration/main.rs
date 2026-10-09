//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Cargo builds this file as one test
//! target and does not build the files next to it on their own. A new test
//! file in this folder needs a `mod` line here; `tools/scripts/check_test_layout.py`
//! fails without one. Helpers that several files use are declared here once,
//! and the files `use crate::<helper>`.
#![allow(clippy::expect_used, clippy::unwrap_used)]

mod detection_precedence_tests;
mod docx_parser_tests;
mod image_parser_tests;
mod magika_detector_tests;
mod magika_timeout_tests;
mod path_traversal_tests;
mod pptx_parser_tests;
mod xlsx_parser_tests;
