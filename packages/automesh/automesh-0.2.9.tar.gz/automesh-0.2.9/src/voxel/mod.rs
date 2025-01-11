#[cfg(feature = "python")]
pub mod py;

#[cfg(test)]
pub mod test;

#[cfg(feature = "profile")]
use std::time::Instant;

use super::{
    fem::{Blocks, HexConnectivity, HexahedralFiniteElements, NODE_NUMBERING_OFFSET},
    Coordinate, Coordinates, Vector, NSD,
};
use conspire::math::TensorArray;
use ndarray::{Array3, Axis};
use ndarray_npy::{ReadNpyError, ReadNpyExt, WriteNpyError, WriteNpyExt};
use std::{
    fs::File,
    io::{BufRead, BufReader, BufWriter, Error, Write},
};
use tiff::{
    decoder::{Decoder, DecodingResult},
    TiffError,
};

type InitialNodalCoordinates = Vec<Option<Coordinate>>;
type Nel = [usize; NSD];
type VoxelDataFlattened = Vec<u8>;
type VoxelDataSized<const N: usize> = Vec<[usize; N]>;

/// The segmentation data corresponding to voxels.
pub type VoxelData = Array3<u8>;

/// The voxels type.
pub struct Voxels {
    data: VoxelData,
}

/// Inherent implementation of the voxels type.
impl Voxels {
    /// Constructs and returns a new voxels type from an NPY file.
    pub fn from_npy(file_path: &str) -> Result<Self, ReadNpyError> {
        Ok(Self {
            data: voxel_data_from_npy(file_path)?,
        })
    }
    /// Constructs and returns a new voxels type from an SPN file.
    pub fn from_spn(file_path: &str, nel: Nel) -> Result<Self, String> {
        Ok(Self {
            data: voxel_data_from_spn(file_path, nel)?,
        })
    }
    /// Constructs and returns a new voxels type from a TIF file.
    pub fn from_tif(file_path: &str) -> Result<Self, String> {
        Ok(Self {
            data: voxel_data_from_tif(file_path)?,
        })
    }
    /// Returns a reference to the internal voxels data.
    pub fn get_data(&self) -> &VoxelData {
        &self.data
    }
    /// Converts the voxels type into a finite elements type, consuming the voxels type.
    pub fn into_finite_elements(
        self,
        remove: Option<Vec<u8>>,
        scale: &Vector,
        translate: &Vector,
    ) -> Result<HexahedralFiniteElements, String> {
        let (element_blocks, element_node_connectivity, nodal_coordinates) =
            finite_element_data_from_data(self.get_data(), remove, scale, translate)?;
        Ok(HexahedralFiniteElements::from_data(
            element_blocks,
            element_node_connectivity,
            nodal_coordinates,
        ))
    }
    /// Writes the internal voxels data to an NPY file.
    pub fn write_npy(&self, file_path: &str) -> Result<(), WriteNpyError> {
        write_voxels_to_npy(self.get_data(), file_path)
    }
    /// Writes the internal voxels data to an SPN file.
    pub fn write_spn(&self, file_path: &str) -> Result<(), Error> {
        write_voxels_to_spn(self.get_data(), file_path)
    }
}

fn filter_voxel_data(data: &VoxelData, remove: Option<Vec<u8>>) -> (VoxelDataSized<NSD>, Blocks) {
    #[cfg(feature = "profile")]
    let time = Instant::now();
    let mut removed_data = remove.unwrap_or_default();
    removed_data.sort();
    removed_data.dedup();
    let filtered_voxel_data_combo: VoxelDataSized<4> = data
        .axis_iter(Axis(2))
        .enumerate()
        .map(|(k, data_k)| {
            data_k
                .axis_iter(Axis(1))
                .enumerate()
                .map(|(j, data_kj)| {
                    data_kj
                        .iter()
                        .enumerate()
                        .filter(|(_, &data_kji)| removed_data.binary_search(&data_kji).is_err())
                        .map(|(i, data_kji)| [i, j, k, *data_kji as usize])
                        .collect()
                })
                .collect()
        })
        .collect::<Vec<Vec<Vec<[usize; 4]>>>>()
        .into_iter()
        .flatten()
        .flatten()
        .collect();
    let element_blocks = filtered_voxel_data_combo
        .iter()
        .map(|entry| entry[3])
        .collect();
    let filtered_voxel_data = filtered_voxel_data_combo
        .into_iter()
        .map(|entry| [entry[0], entry[1], entry[2]])
        .collect();
    #[cfg(feature = "profile")]
    println!(
        "           \x1b[1;93m⤷ Removed voxels\x1b[0m {:?}",
        time.elapsed()
    );
    (filtered_voxel_data, element_blocks)
}

fn initial_element_node_connectivity(
    filtered_voxel_data: &VoxelDataSized<NSD>,
    nelxplus1: &usize,
    nelyplus1: &usize,
) -> HexConnectivity {
    #[cfg(feature = "profile")]
    let time = Instant::now();
    let element_node_connectivity: HexConnectivity = filtered_voxel_data
        .iter()
        .map(|entry| {
            [
                entry[0]
                    + entry[1] * nelxplus1
                    + entry[2] * nelxplus1 * nelyplus1
                    + NODE_NUMBERING_OFFSET,
                entry[0]
                    + entry[1] * nelxplus1
                    + entry[2] * nelxplus1 * nelyplus1
                    + 1
                    + NODE_NUMBERING_OFFSET,
                entry[0]
                    + (entry[1] + 1) * nelxplus1
                    + entry[2] * nelxplus1 * nelyplus1
                    + 1
                    + NODE_NUMBERING_OFFSET,
                entry[0]
                    + (entry[1] + 1) * nelxplus1
                    + entry[2] * nelxplus1 * nelyplus1
                    + NODE_NUMBERING_OFFSET,
                entry[0]
                    + entry[1] * nelxplus1
                    + (entry[2] + 1) * nelxplus1 * nelyplus1
                    + NODE_NUMBERING_OFFSET,
                entry[0]
                    + entry[1] * nelxplus1
                    + (entry[2] + 1) * nelxplus1 * nelyplus1
                    + 1
                    + NODE_NUMBERING_OFFSET,
                entry[0]
                    + (entry[1] + 1) * nelxplus1
                    + (entry[2] + 1) * nelxplus1 * nelyplus1
                    + 1
                    + NODE_NUMBERING_OFFSET,
                entry[0]
                    + (entry[1] + 1) * nelxplus1
                    + (entry[2] + 1) * nelxplus1 * nelyplus1
                    + NODE_NUMBERING_OFFSET,
            ]
        })
        .collect();
    #[cfg(feature = "profile")]
    println!(
        "             \x1b[1;93mElement-to-node connectivity\x1b[0m {:?}",
        time.elapsed()
    );
    element_node_connectivity
}

fn initial_nodal_coordinates(
    element_node_connectivity: &HexConnectivity,
    filtered_voxel_data: &VoxelDataSized<NSD>,
    number_of_nodes_unfiltered: usize,
    scale: &Vector,
    translate: &Vector,
) -> Result<InitialNodalCoordinates, String> {
    #[cfg(feature = "profile")]
    let time = Instant::now();
    let xscale = scale[0];
    let yscale = scale[1];
    let zscale = scale[2];
    let xtranslate = translate[0];
    let ytranslate = translate[1];
    let ztranslate: f64 = translate[2];
    let mut nodal_coordinates: InitialNodalCoordinates =
        (0..number_of_nodes_unfiltered).map(|_| None).collect();
    if xscale <= 0.0 {
        Err("Need to specify xscale > 0.0".to_string())
    } else if yscale <= 0.0 {
        Err("Need to specify yscale > 0.0".to_string())
    } else if zscale <= 0.0 {
        Err("Need to specify zscale > 0.0".to_string())
    } else {
        filtered_voxel_data
            .iter()
            .zip(element_node_connectivity.iter())
            .for_each(|(entry, connectivity)| {
                nodal_coordinates[connectivity[0] - NODE_NUMBERING_OFFSET] =
                    Some(Coordinate::new([
                        (entry[0] as f64) * xscale + xtranslate,
                        (entry[1] as f64) * yscale + ytranslate,
                        (entry[2] as f64) * zscale + ztranslate,
                    ]));
                nodal_coordinates[connectivity[1] - NODE_NUMBERING_OFFSET] =
                    Some(Coordinate::new([
                        (entry[0] as f64 + 1.0) * xscale + xtranslate,
                        (entry[1] as f64) * yscale + ytranslate,
                        (entry[2] as f64) * zscale + ztranslate,
                    ]));
                nodal_coordinates[connectivity[2] - NODE_NUMBERING_OFFSET] =
                    Some(Coordinate::new([
                        (entry[0] as f64 + 1.0) * xscale + xtranslate,
                        (entry[1] as f64 + 1.0) * yscale + ytranslate,
                        (entry[2] as f64) * zscale + ztranslate,
                    ]));
                nodal_coordinates[connectivity[3] - NODE_NUMBERING_OFFSET] =
                    Some(Coordinate::new([
                        (entry[0] as f64) * xscale + xtranslate,
                        (entry[1] as f64 + 1.0) * yscale + ytranslate,
                        (entry[2] as f64) * zscale + ztranslate,
                    ]));
                nodal_coordinates[connectivity[4] - NODE_NUMBERING_OFFSET] =
                    Some(Coordinate::new([
                        (entry[0] as f64) * xscale + xtranslate,
                        (entry[1] as f64) * yscale + ytranslate,
                        (entry[2] as f64 + 1.0) * zscale + ztranslate,
                    ]));
                nodal_coordinates[connectivity[5] - NODE_NUMBERING_OFFSET] =
                    Some(Coordinate::new([
                        (entry[0] as f64 + 1.0) * xscale + xtranslate,
                        (entry[1] as f64) * yscale + ytranslate,
                        (entry[2] as f64 + 1.0) * zscale + ztranslate,
                    ]));
                nodal_coordinates[connectivity[6] - NODE_NUMBERING_OFFSET] =
                    Some(Coordinate::new([
                        (entry[0] as f64 + 1.0) * xscale + xtranslate,
                        (entry[1] as f64 + 1.0) * yscale + ytranslate,
                        (entry[2] as f64 + 1.0) * zscale + ztranslate,
                    ]));
                nodal_coordinates[connectivity[7] - NODE_NUMBERING_OFFSET] =
                    Some(Coordinate::new([
                        (entry[0] as f64) * xscale + xtranslate,
                        (entry[1] as f64 + 1.0) * yscale + ytranslate,
                        (entry[2] as f64 + 1.0) * zscale + ztranslate,
                    ]));
            });
        #[cfg(feature = "profile")]
        println!(
            "             \x1b[1;93mNodal coordinates\x1b[0m {:?}",
            time.elapsed()
        );
        Ok(nodal_coordinates)
    }
}

fn renumber_nodes(
    element_node_connectivity: &mut HexConnectivity,
    mut initial_nodal_coordinates: InitialNodalCoordinates,
    number_of_nodes_unfiltered: usize,
) -> Coordinates {
    #[cfg(feature = "profile")]
    let time = std::time::Instant::now();
    let mut mapping = vec![0; number_of_nodes_unfiltered];
    let mut nodes = 1..=number_of_nodes_unfiltered;
    initial_nodal_coordinates
        .iter()
        .enumerate()
        .filter(|&(_, coordinate)| coordinate.is_some())
        .for_each(|(index, _)| {
            if let Some(node) = nodes.next() {
                mapping[index] = node;
            }
        });
    element_node_connectivity
        .iter_mut()
        .for_each(|connectivity| {
            connectivity
                .iter_mut()
                .for_each(|node| *node = mapping[*node - NODE_NUMBERING_OFFSET])
        });
    initial_nodal_coordinates.retain(|coordinate| coordinate.is_some());
    let nodal_coordinates = initial_nodal_coordinates
        .into_iter()
        .map(|entry| entry.unwrap())
        .collect();
    #[cfg(feature = "profile")]
    println!(
        "             \x1b[1;93mRenumbered nodes\x1b[0m {:?}",
        time.elapsed()
    );
    nodal_coordinates
}

fn finite_element_data_from_data(
    data: &VoxelData,
    remove: Option<Vec<u8>>,
    scale: &Vector,
    translate: &Vector,
) -> Result<(Blocks, HexConnectivity, Coordinates), String> {
    let shape = data.shape();
    let nelxplus1 = shape[0] + 1;
    let nelyplus1 = shape[1] + 1;
    let nelzplus1 = shape[2] + 1;
    let number_of_nodes_unfiltered = nelxplus1 * nelyplus1 * nelzplus1;
    let (filtered_voxel_data, element_blocks) = filter_voxel_data(data, remove);
    let mut element_node_connectivity =
        initial_element_node_connectivity(&filtered_voxel_data, &nelxplus1, &nelyplus1);
    let initial_nodal_coordinates = initial_nodal_coordinates(
        &element_node_connectivity,
        &filtered_voxel_data,
        number_of_nodes_unfiltered,
        scale,
        translate,
    )?;
    let nodal_coordinates = renumber_nodes(
        &mut element_node_connectivity,
        initial_nodal_coordinates,
        number_of_nodes_unfiltered,
    );
    Ok((element_blocks, element_node_connectivity, nodal_coordinates))
}

pub struct IntermediateError {
    pub message: String,
}

impl From<Error> for IntermediateError {
    fn from(error: Error) -> IntermediateError {
        IntermediateError {
            message: error.to_string(),
        }
    }
}

impl From<IntermediateError> for String {
    fn from(err: IntermediateError) -> String {
        err.message
    }
}

impl From<String> for IntermediateError {
    fn from(error: String) -> IntermediateError {
        IntermediateError { message: error }
    }
}

impl From<TiffError> for IntermediateError {
    fn from(error: TiffError) -> IntermediateError {
        IntermediateError {
            message: error.to_string(),
        }
    }
}

fn voxel_data_from_npy(file_path: &str) -> Result<VoxelData, ReadNpyError> {
    VoxelData::read_npy(File::open(file_path)?)
}

fn voxel_data_from_spn(file_path: &str, nel: Nel) -> Result<VoxelData, IntermediateError> {
    if nel[0] < 1 {
        Err("Need to specify nelx > 0".to_string())?
    } else if nel[1] < 1 {
        Err("Need to specify nely > 0".to_string())?
    } else if nel[2] < 1 {
        Err("Need to specify nelz > 0".to_string())?
    } else {
        let data_flattened = BufReader::new(File::open(file_path)?)
            .lines()
            .map(|line| line.unwrap().parse().unwrap())
            .collect::<VoxelDataFlattened>();
        let mut data = VoxelData::zeros((nel[0], nel[1], nel[2]));
        data.axis_iter_mut(Axis(2))
            .enumerate()
            .for_each(|(k, mut data_k)| {
                data_k
                    .axis_iter_mut(Axis(1))
                    .enumerate()
                    .for_each(|(j, mut data_jk)| {
                        data_jk.iter_mut().enumerate().for_each(|(i, data_ijk)| {
                            *data_ijk = data_flattened[i + nel[0] * j + nel[0] * nel[1] * k]
                        })
                    })
            });
        Ok(data)
    }
}

fn voxel_data_from_tif(file_path: &str) -> Result<VoxelData, IntermediateError> {
    let mut file = std::path::PathBuf::from(file_path);
    let file_stem = file
        .file_stem()
        .ok_or("asdf".to_string())?
        .to_str()
        .ok_or("asdf".to_string())?
        .to_string();
    let file_extension = file
        .extension()
        .ok_or("asdf".to_string())?
        .to_str()
        .ok_or("asdf".to_string())?
        .to_string();
    let basic_file_path = format!(
        "{}/{}",
        file.parent()
            .ok_or("asdf".to_string())?
            .to_str()
            .ok_or("asdf".to_string())?,
        file_stem
    );
    file.set_file_name(format!("{}_0.{}", file_stem, file_extension));
    let mut decoder = Decoder::new(BufReader::new(File::open(
        file.to_str().ok_or("asdf".to_string())?,
    )?))?;
    let (mut nelx, mut nely) = decoder.dimensions()?;
    let mut index = 0;
    while file.exists() {
        index += 1;
        file.set_file_name(format!("{}_{}.{}", file_stem, index, file_extension));
    }
    let nel: Nel = [nelx as usize, nely as usize, index as usize];
    let mut data = VoxelData::zeros((nel[0], nel[1], nel[2]));
    data.axis_iter_mut(Axis(2))
        .enumerate()
        .try_for_each(|(k, mut data_k)| {
            decoder = Decoder::new(BufReader::new(File::open(format!(
                "{}_{}.{}",
                basic_file_path, k, file_extension
            ))?))?;
            (nelx, nely) = decoder.dimensions()?;
            if nel[0] != nelx as usize || nel[1] != nely as usize {
                panic!()
            }
            match decoder.read_image()? {
                DecodingResult::U8(data_flattened) => data_flattened,
                _ => panic!(),
            }
            .chunks(nel[0])
            .zip(data_k.axis_iter_mut(Axis(1)).rev())
            .for_each(|(chunk, mut data_kj)| {
                chunk
                    .iter()
                    .zip(data_kj.iter_mut())
                    .for_each(|(a, data_kji)| *data_kji = *a)
            });
            Ok::<(), IntermediateError>(())
        })?;
    Ok(data)
}

fn write_voxels_to_npy(data: &VoxelData, file_path: &str) -> Result<(), WriteNpyError> {
    data.write_npy(BufWriter::new(File::create(file_path)?))
}

fn write_voxels_to_spn(data: &VoxelData, file_path: &str) -> Result<(), Error> {
    let mut file = BufWriter::new(File::create(file_path)?);
    data.axis_iter(Axis(2)).try_for_each(|entry_2d| {
        entry_2d
            .axis_iter(Axis(1))
            .flatten()
            .try_for_each(|entry| writeln!(file, "{}", entry))
    })
}
