//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Cargo builds this file as one test
//! target and does not build the files next to it on their own. A new test
//! file in this folder needs a `mod` line here; `tools/scripts/check_test_layout.py`
//! fails without one. Helpers that several files use are declared here once,
//! and the files `use crate::<helper>`.

mod protogen_shape;
// By path, so the `mod` lines inside it look in this folder, as they did when
// it was a crate root of its own.
#[path = "watch_lifecycle.rs"]
mod watch_lifecycle;
