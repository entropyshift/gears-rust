//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.

#[path = "crypto_init.rs"]
mod crypto_init;
#[path = "crypto_init_fips.rs"]
mod crypto_init_fips;
#[path = "db_phase_tests.rs"]
mod db_phase_tests;
// Its `pub` demo types were used as the root of their own binary.
#[allow(dead_code)]
#[path = "domain_enforcement_demo.rs"]
mod domain_enforcement_demo;
#[path = "domain_model_tests.rs"]
mod domain_model_tests;
#[path = "extractor_order_with_cursor.rs"]
mod extractor_order_with_cursor;
#[path = "integration_test.rs"]
mod integration_test;
#[path = "lifecycle_macro_tests.rs"]
mod lifecycle_macro_tests;
#[path = "lifecycle_state.rs"]
mod lifecycle_state;
#[path = "macro_tests.rs"]
mod macro_tests;
#[path = "odata_select.rs"]
mod odata_select;
#[path = "panic_tracing_tests.rs"]
mod panic_tracing_tests;
#[path = "runner_tests.rs"]
mod runner_tests;
#[path = "typed_builder_compilefail.rs"]
mod typed_builder_compilefail;
