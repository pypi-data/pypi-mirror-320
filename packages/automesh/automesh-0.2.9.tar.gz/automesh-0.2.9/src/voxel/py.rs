use super::{
    super::{
        fem::py::FiniteElements,
        py::{IntoFoo, PyIntermediateError},
    },
    finite_element_data_from_data, voxel_data_from_npy, voxel_data_from_spn, write_voxels_to_npy,
    write_voxels_to_spn, Nel, Vector, VoxelData,
};
use conspire::math::TensorArray;
use pyo3::prelude::*;

pub fn register_module(parent_module: &Bound<'_, PyModule>) -> PyResult<()> {
    parent_module.add_class::<Voxels>()?;
    Ok(())
}

/// The voxels class.
#[pyclass]
pub struct Voxels {
    data: VoxelData,
}

#[pymethods]
impl Voxels {
    /// Converts the voxels type into a finite elements type.
    #[pyo3(signature = (remove=[].to_vec(), scale=[1.0, 1.0, 1.0], translate=[0.0, 0.0, 0.0]))]
    pub fn as_finite_elements(
        &self,
        remove: Option<Vec<u8>>,
        scale: [f64; 3],
        translate: [f64; 3],
    ) -> Result<FiniteElements, PyIntermediateError> {
        let (element_blocks, element_node_connectivity, nodal_coordinates) =
            finite_element_data_from_data(
                &self.data,
                remove,
                &Vector::new(scale),
                &Vector::new(translate),
            )?;
        Ok(FiniteElements::from_data(
            element_blocks,
            element_node_connectivity,
            nodal_coordinates.as_foo(),
        ))
    }
    /// Constructs and returns a new voxels type from an NPY file.
    #[staticmethod]
    pub fn from_npy(file_path: &str) -> Result<Self, PyIntermediateError> {
        Ok(Self {
            data: voxel_data_from_npy(file_path)?,
        })
    }
    /// Constructs and returns a new voxels type from an SPN file.
    #[staticmethod]
    pub fn from_spn(file_path: &str, nel: Nel) -> Result<Self, PyIntermediateError> {
        Ok(Self {
            data: voxel_data_from_spn(file_path, nel)?,
        })
    }
    /// Writes the internal voxels data to an NPY file.
    pub fn write_npy(&self, file_path: &str) -> Result<(), PyIntermediateError> {
        Ok(write_voxels_to_npy(&self.data, file_path)?)
    }
    /// Writes the internal voxels data to an SPN file.
    pub fn write_spn(&self, file_path: &str) -> Result<(), PyIntermediateError> {
        Ok(write_voxels_to_spn(&self.data, file_path)?)
    }
}
