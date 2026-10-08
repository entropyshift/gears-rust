//! Every integration test of this crate in one binary, so they compile and
//! link once instead of once per file. Each file stays where it is and is
//! loaded as a module (`autotests = false` in Cargo.toml). A new test file
//! needs a `#[path]` line here; `tools/scripts/check_test_layout.py` fails
//! without one. Helpers that several files use are declared here once, and
//! the files `use crate::<helper>`.

mod common;

#[path = "catalog_integration_pg.rs"]
mod catalog_integration_pg;
#[path = "cleanup_integration_pg.rs"]
mod cleanup_integration_pg;
#[path = "id_uniqueness_integration_pg.rs"]
mod id_uniqueness_integration_pg;
#[path = "records_ingest_integration_pg.rs"]
mod records_ingest_integration_pg;
#[path = "records_query_integration_pg.rs"]
mod records_query_integration_pg;
#[path = "schema_integration_pg.rs"]
mod schema_integration_pg;
