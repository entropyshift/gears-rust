//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.

#[path = "third_party_base_url.rs"]
mod third_party_base_url;
#[path = "third_party_custom_transport.rs"]
mod third_party_custom_transport;
#[path = "third_party_in_process.rs"]
mod third_party_in_process;
#[path = "usage.rs"]
mod usage;
