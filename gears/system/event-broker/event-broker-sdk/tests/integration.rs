//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.

// The file wraps its tests in a `mod consumer` of its own.
#[allow(clippy::module_inception)]
#[path = "consumer.rs"]
mod consumer;
#[path = "producer.rs"]
mod producer;
#[path = "rest_roundtrip.rs"]
mod rest_roundtrip;
// The file wraps its tests in a `mod sdk` of its own.
#[allow(clippy::module_inception)]
#[path = "sdk.rs"]
mod sdk;
#[path = "usage.rs"]
mod usage;
