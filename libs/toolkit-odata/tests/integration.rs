//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.
#![allow(clippy::expect_used, clippy::unwrap_used)]

#[path = "convert.rs"]
mod convert;
#[path = "field_operators.rs"]
mod field_operators;
#[path = "null_equality.rs"]
mod null_equality;
#[path = "order_roundtrip.rs"]
mod order_roundtrip;
