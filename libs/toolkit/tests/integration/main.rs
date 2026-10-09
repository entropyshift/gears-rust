//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Cargo builds this file as one test
//! target and does not build the files next to it on their own. A new test
//! file in this folder needs a `mod` line here; `tools/scripts/check_test_layout.py`
//! fails without one. Helpers that several files use are declared here once,
//! and the files `use crate::<helper>`.

mod crypto_init;
mod crypto_init_fips;
mod db_phase_tests;
// Its `pub` demo types were used as the root of their own binary.
#[allow(dead_code)]
mod domain_enforcement_demo;
mod domain_model_tests;
mod extractor_order_with_cursor;
mod integration_test;
mod lifecycle_macro_tests;
mod lifecycle_state;
mod odata_select;
mod panic_tracing_tests;
mod runner_tests;
mod typed_builder_compilefail;
