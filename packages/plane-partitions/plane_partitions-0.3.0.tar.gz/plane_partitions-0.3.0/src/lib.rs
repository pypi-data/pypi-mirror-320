use plane_partition::PlanePartition;
use pyo3::prelude::*;

pub mod plane_partition;

/// Prints the package version
#[pyfunction]
fn version() -> PyResult<String> {
    Ok(env!("CARGO_PKG_VERSION").to_string())
}

///Python module for working with plane plane partitions
///Written by Jimmy Ostler <jtostler1@gmail.com>
#[pymodule]
fn plane_partitions(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(version, m)?)?;
    m.add_class::<PlanePartition>()?;
    Ok(())
}
