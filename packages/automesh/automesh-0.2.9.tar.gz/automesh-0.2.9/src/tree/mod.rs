#[cfg(feature = "profile")]
use std::time::Instant;

use super::{
    fem::{NODE_NUMBERING_OFFSET, NUM_NODES_HEX},
    Coordinate, Coordinates, HexahedralFiniteElements, Vector, VoxelData, Voxels,
};
use conspire::math::{Tensor, TensorArray, TensorVec};
use ndarray::{s, Axis};
use std::array::from_fn;

const NUM_FACES: usize = 6;
const NUM_OCTANTS: usize = 8;

type Cells = [Cell; NUM_OCTANTS];
type Faces = [Option<usize>; NUM_FACES];
type Indices = [usize; NUM_OCTANTS];

/// The octree type.
pub type Octree = Vec<Cell>;

/// Methods for trees such as quadtrees or octrees.
pub trait Tree {
    fn balance(&mut self, strong: bool);
    fn from_voxels(voxels: Voxels) -> Self;
    fn into_finite_elements(
        self,
        remove: Option<Vec<u8>>,
        scale: &Vector,
        translate: &Vector,
    ) -> Result<HexahedralFiniteElements, String>;
    fn octree_into_finite_elements(
        self,
        remove: Option<Vec<u8>>,
        scale: &Vector,
        translate: &Vector,
    ) -> Result<HexahedralFiniteElements, String>;
    fn pair(&mut self);
    fn prune(&mut self);
    fn subdivide(&mut self, index: usize);
}

#[derive(Debug)]
pub struct Cell {
    block: Option<u8>,
    cells: Option<Indices>,
    faces: Faces,
    level: usize,
    min_x: f64,
    max_x: f64,
    min_y: f64,
    max_y: f64,
    min_z: f64,
    max_z: f64,
}

impl Cell {
    fn get_block(&self) -> u8 {
        if let Some(block) = self.block {
            block
        } else {
            panic!()
        }
    }
    fn get_cells(&self) -> &Option<Indices> {
        &self.cells
    }
    fn get_faces(&self) -> &Faces {
        &self.faces
    }
    fn get_level(&self) -> &usize {
        &self.level
    }
    fn get_min_x(&self) -> &f64 {
        &self.min_x
    }
    fn get_max_x(&self) -> &f64 {
        &self.max_x
    }
    fn get_min_y(&self) -> &f64 {
        &self.min_y
    }
    fn get_max_y(&self) -> &f64 {
        &self.max_y
    }
    fn get_min_z(&self) -> &f64 {
        &self.min_z
    }
    fn get_max_z(&self) -> &f64 {
        &self.max_z
    }
    fn homogeneous(&self, data: &VoxelData) -> Option<u8> {
        let x_min = self.get_min_x().round() as u8 as usize;
        let x_max = self.get_max_x().round() as u8 as usize;
        let y_min = self.get_min_y().round() as u8 as usize;
        let y_max = self.get_max_y().round() as u8 as usize;
        let z_min = self.get_min_z().round() as u8 as usize;
        let z_max = self.get_max_z().round() as u8 as usize;
        let contained = data.slice(s![x_min..x_max, y_min..y_max, z_min..z_max]);
        let mut materials: Vec<u8> = contained.iter().cloned().collect();
        materials.dedup();
        if materials.len() == 1 {
            Some(materials[0])
        } else {
            None
        }
    }
    fn subdivide(&mut self, indices: Indices) -> Cells {
        self.cells = Some(indices);
        let level = self.get_level() + 1;
        let min_x = self.get_min_x();
        let max_x = self.get_max_x();
        let min_y = self.get_min_y();
        let max_y = self.get_max_y();
        let min_z = self.get_min_z();
        let max_z = self.get_max_z();
        let val_x = 0.5 * (min_x + max_x);
        let val_y = 0.5 * (min_y + max_y);
        let val_z = 0.5 * (min_z + max_z);
        [
            Cell {
                block: None,
                cells: None,
                faces: [
                    None,
                    Some(indices[1]),
                    Some(indices[2]),
                    None,
                    None,
                    Some(indices[4]),
                ],
                level,
                min_x: *min_x,
                max_x: val_x,
                min_y: *min_y,
                max_y: val_y,
                min_z: *min_z,
                max_z: val_z,
            },
            Cell {
                block: None,
                cells: None,
                faces: [
                    None,
                    None,
                    Some(indices[3]),
                    Some(indices[0]),
                    None,
                    Some(indices[5]),
                ],
                level,
                min_x: val_x,
                max_x: *max_x,
                min_y: *min_y,
                max_y: val_y,
                min_z: *min_z,
                max_z: val_z,
            },
            Cell {
                block: None,
                cells: None,
                faces: [
                    Some(indices[0]),
                    Some(indices[3]),
                    None,
                    None,
                    None,
                    Some(indices[6]),
                ],
                level,
                min_x: *min_x,
                max_x: val_x,
                min_y: val_y,
                max_y: *max_y,
                min_z: *min_z,
                max_z: val_z,
            },
            Cell {
                block: None,
                cells: None,
                faces: [
                    Some(indices[1]),
                    None,
                    None,
                    Some(indices[2]),
                    None,
                    Some(indices[7]),
                ],
                level,
                min_x: val_x,
                max_x: *max_x,
                min_y: val_y,
                max_y: *max_y,
                min_z: *min_z,
                max_z: val_z,
            },
            Cell {
                block: None,
                cells: None,
                faces: [
                    None,
                    Some(indices[5]),
                    Some(indices[6]),
                    None,
                    Some(indices[0]),
                    None,
                ],
                level,
                min_x: *min_x,
                max_x: val_x,
                min_y: *min_y,
                max_y: val_y,
                min_z: val_z,
                max_z: *max_z,
            },
            Cell {
                block: None,
                cells: None,
                faces: [
                    None,
                    None,
                    Some(indices[7]),
                    Some(indices[4]),
                    Some(indices[1]),
                    None,
                ],
                level,
                min_x: val_x,
                max_x: *max_x,
                min_y: *min_y,
                max_y: val_y,
                min_z: val_z,
                max_z: *max_z,
            },
            Cell {
                block: None,
                cells: None,
                faces: [
                    Some(indices[4]),
                    Some(indices[7]),
                    None,
                    None,
                    Some(indices[2]),
                    None,
                ],
                level,
                min_x: *min_x,
                max_x: val_x,
                min_y: val_y,
                max_y: *max_y,
                min_z: val_z,
                max_z: *max_z,
            },
            Cell {
                block: None,
                cells: None,
                faces: [
                    Some(indices[5]),
                    None,
                    None,
                    Some(indices[6]),
                    Some(indices[3]),
                    None,
                ],
                level,
                min_x: val_x,
                max_x: *max_x,
                min_y: val_y,
                max_y: *max_y,
                min_z: val_z,
                max_z: *max_z,
            },
        ]
    }
}

impl Tree for Octree {
    fn balance(&mut self, strong: bool) {
        let mut balanced;
        let mut block;
        let mut edges: [bool; 8];
        let mut index;
        let mut subdivide;
        let levels = *self[self.len() - 1].get_level();
        #[allow(unused_variables)]
        for iteration in 1.. {
            balanced = true;
            index = 0;
            subdivide = false;
            #[cfg(feature = "profile")]
            let time = Instant::now();
            while index < self.len() {
                if self[index].get_level() < &(levels - 1) && self[index].cells.is_none() {
                    'faces: for (face, face_cell) in self[index].get_faces().iter().enumerate() {
                        if let Some(neighbor) = face_cell {
                            if let Some(kids) = self[*neighbor].cells {
                                edges = from_fn(|_| false);
                                if match face {
                                    0 => {
                                        if strong {
                                            if let Some(edge_cell) = self[kids[3]].get_faces()[1] {
                                                edges[0] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[0] = false
                                            }
                                            if let Some(edge_cell) = self[kids[7]].get_faces()[1] {
                                                edges[1] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[1] = false
                                            }
                                            if let Some(edge_cell) = self[kids[6]].get_faces()[5] {
                                                edges[2] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[2] = false
                                            }
                                            if let Some(edge_cell) = self[kids[7]].get_faces()[5] {
                                                edges[3] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[3] = false
                                            }
                                            if let Some(edge_cell) = self[kids[2]].get_faces()[3] {
                                                edges[4] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[4] = false
                                            }
                                            if let Some(edge_cell) = self[kids[6]].get_faces()[3] {
                                                edges[5] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[5] = false
                                            }
                                            if let Some(edge_cell) = self[kids[2]].get_faces()[4] {
                                                edges[6] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[6] = false
                                            }
                                            if let Some(edge_cell) = self[kids[3]].get_faces()[4] {
                                                edges[7] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[7] = false
                                            }
                                        }
                                        edges.into_iter().any(|edge| edge)
                                            || self[kids[2]].cells.is_some()
                                            || self[kids[3]].cells.is_some()
                                            || self[kids[6]].cells.is_some()
                                            || self[kids[7]].cells.is_some()
                                    }
                                    1 => {
                                        if strong {
                                            if let Some(edge_cell) = self[kids[2]].get_faces()[2] {
                                                edges[0] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[0] = false
                                            }
                                            if let Some(edge_cell) = self[kids[6]].get_faces()[2] {
                                                edges[1] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[1] = false
                                            }
                                            if let Some(edge_cell) = self[kids[4]].get_faces()[5] {
                                                edges[2] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[2] = false
                                            }
                                            if let Some(edge_cell) = self[kids[6]].get_faces()[5] {
                                                edges[3] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[3] = false
                                            }
                                            if let Some(edge_cell) = self[kids[0]].get_faces()[0] {
                                                edges[4] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[4] = false
                                            }
                                            if let Some(edge_cell) = self[kids[4]].get_faces()[0] {
                                                edges[5] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[5] = false
                                            }
                                            if let Some(edge_cell) = self[kids[0]].get_faces()[4] {
                                                edges[6] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[6] = false
                                            }
                                            if let Some(edge_cell) = self[kids[2]].get_faces()[4] {
                                                edges[7] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[7] = false
                                            }
                                        }
                                        edges.into_iter().any(|edge| edge)
                                            || self[kids[0]].cells.is_some()
                                            || self[kids[2]].cells.is_some()
                                            || self[kids[4]].cells.is_some()
                                            || self[kids[6]].cells.is_some()
                                    }
                                    2 => {
                                        if strong {
                                            if let Some(edge_cell) = self[kids[0]].get_faces()[3] {
                                                edges[0] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[0] = false
                                            }
                                            if let Some(edge_cell) = self[kids[4]].get_faces()[3] {
                                                edges[1] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[1] = false
                                            }
                                            if let Some(edge_cell) = self[kids[4]].get_faces()[5] {
                                                edges[2] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[2] = false
                                            }
                                            if let Some(edge_cell) = self[kids[5]].get_faces()[5] {
                                                edges[3] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[3] = false
                                            }
                                            if let Some(edge_cell) = self[kids[1]].get_faces()[1] {
                                                edges[4] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[4] = false
                                            }
                                            if let Some(edge_cell) = self[kids[5]].get_faces()[1] {
                                                edges[5] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[5] = false
                                            }
                                            if let Some(edge_cell) = self[kids[0]].get_faces()[4] {
                                                edges[6] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[6] = false
                                            }
                                            if let Some(edge_cell) = self[kids[1]].get_faces()[4] {
                                                edges[7] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[7] = false
                                            }
                                        }
                                        edges.into_iter().any(|edge| edge)
                                            || self[kids[0]].cells.is_some()
                                            || self[kids[1]].cells.is_some()
                                            || self[kids[4]].cells.is_some()
                                            || self[kids[5]].cells.is_some()
                                    }
                                    3 => {
                                        if strong {
                                            if let Some(edge_cell) = self[kids[1]].get_faces()[0] {
                                                edges[0] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[0] = false
                                            }
                                            if let Some(edge_cell) = self[kids[5]].get_faces()[0] {
                                                edges[1] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[1] = false
                                            }
                                            if let Some(edge_cell) = self[kids[5]].get_faces()[5] {
                                                edges[2] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[2] = false
                                            }
                                            if let Some(edge_cell) = self[kids[7]].get_faces()[5] {
                                                edges[3] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[3] = false
                                            }
                                            if let Some(edge_cell) = self[kids[3]].get_faces()[2] {
                                                edges[4] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[4] = false
                                            }
                                            if let Some(edge_cell) = self[kids[7]].get_faces()[2] {
                                                edges[5] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[5] = false
                                            }
                                            if let Some(edge_cell) = self[kids[1]].get_faces()[4] {
                                                edges[6] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[6] = false
                                            }
                                            if let Some(edge_cell) = self[kids[3]].get_faces()[4] {
                                                edges[7] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[7] = false
                                            }
                                        }
                                        edges.into_iter().any(|edge| edge)
                                            || self[kids[1]].cells.is_some()
                                            || self[kids[3]].cells.is_some()
                                            || self[kids[5]].cells.is_some()
                                            || self[kids[7]].cells.is_some()
                                    }
                                    4 => {
                                        if strong {
                                            if let Some(edge_cell) = self[kids[5]].get_faces()[1] {
                                                edges[0] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[0] = false
                                            }
                                            if let Some(edge_cell) = self[kids[7]].get_faces()[1] {
                                                edges[1] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[1] = false
                                            }
                                            if let Some(edge_cell) = self[kids[6]].get_faces()[2] {
                                                edges[2] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[2] = false
                                            }
                                            if let Some(edge_cell) = self[kids[7]].get_faces()[2] {
                                                edges[3] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[3] = false
                                            }
                                            if let Some(edge_cell) = self[kids[4]].get_faces()[3] {
                                                edges[4] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[4] = false
                                            }
                                            if let Some(edge_cell) = self[kids[6]].get_faces()[3] {
                                                edges[5] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[5] = false
                                            }
                                            if let Some(edge_cell) = self[kids[4]].get_faces()[0] {
                                                edges[6] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[6] = false
                                            }
                                            if let Some(edge_cell) = self[kids[5]].get_faces()[0] {
                                                edges[7] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[7] = false
                                            }
                                        }
                                        edges.into_iter().any(|edge| edge)
                                            || self[kids[4]].cells.is_some()
                                            || self[kids[5]].cells.is_some()
                                            || self[kids[6]].cells.is_some()
                                            || self[kids[7]].cells.is_some()
                                    }
                                    5 => {
                                        if strong {
                                            if let Some(edge_cell) = self[kids[1]].get_faces()[1] {
                                                edges[0] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[0] = false
                                            }
                                            if let Some(edge_cell) = self[kids[3]].get_faces()[1] {
                                                edges[1] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[1] = false
                                            }
                                            if let Some(edge_cell) = self[kids[2]].get_faces()[2] {
                                                edges[2] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[2] = false
                                            }
                                            if let Some(edge_cell) = self[kids[3]].get_faces()[2] {
                                                edges[3] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[3] = false
                                            }
                                            if let Some(edge_cell) = self[kids[0]].get_faces()[3] {
                                                edges[4] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[4] = false
                                            }
                                            if let Some(edge_cell) = self[kids[2]].get_faces()[3] {
                                                edges[5] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[5] = false
                                            }
                                            if let Some(edge_cell) = self[kids[0]].get_faces()[0] {
                                                edges[6] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[6] = false
                                            }
                                            if let Some(edge_cell) = self[kids[1]].get_faces()[0] {
                                                edges[7] = self[edge_cell].cells.is_some()
                                            } else {
                                                edges[7] = false
                                            }
                                        }
                                        edges.into_iter().any(|edge| edge)
                                            || self[kids[0]].cells.is_some()
                                            || self[kids[1]].cells.is_some()
                                            || self[kids[2]].cells.is_some()
                                            || self[kids[3]].cells.is_some()
                                    }
                                    _ => panic!(),
                                } {
                                    subdivide = true;
                                    break 'faces;
                                }
                            }
                        }
                    }
                    if subdivide {
                        block = self[index].get_block();
                        self.subdivide(index);
                        self.iter_mut()
                            .rev()
                            .take(NUM_OCTANTS)
                            .for_each(|cell| cell.block = Some(block));
                        balanced = false;
                        subdivide = false;
                    }
                }
                index += 1;
            }
            #[cfg(feature = "profile")]
            println!(
                "             \x1b[1;93mBalancing iteration {}\x1b[0m {:?} ",
                iteration,
                time.elapsed()
            );
            if balanced {
                break;
            }
        }
    }
    fn from_voxels(voxels: Voxels) -> Self {
        #[cfg(feature = "profile")]
        let time = Instant::now();
        let data_voxels = voxels.get_data();
        let mut nels = [0; 3];
        nels.iter_mut()
            .zip(data_voxels.shape().iter())
            .for_each(|(nel, nel_0)| {
                *nel = *nel_0;
                while (*nel & (*nel - 1)) != 0 {
                    *nel += 1
                }
            });
        let mut data = VoxelData::zeros((nels[0], nels[1], nels[2]));
        data.axis_iter_mut(Axis(2))
            .zip(data_voxels.axis_iter(Axis(2)))
            .for_each(|(mut data_i, data_voxels_i)| {
                data_i
                    .axis_iter_mut(Axis(1))
                    .zip(data_voxels_i.axis_iter(Axis(1)))
                    .for_each(|(mut data_ij, data_voxels_ij)| {
                        data_ij
                            .iter_mut()
                            .zip(data_voxels_ij.iter())
                            .for_each(|(data_ijk, data_voxels_ijk)| *data_ijk = *data_voxels_ijk)
                    })
            });
        let nel_min = nels.iter().min().unwrap();
        let length = *nel_min as f64;
        let mut tree = vec![];
        (0..(nels[0] / nel_min)).for_each(|i| {
            (0..(nels[1] / nel_min)).for_each(|j| {
                (0..(nels[2] / nel_min)).for_each(|k| {
                    tree.push(Cell {
                        block: None,
                        cells: None,
                        faces: [None; NUM_FACES],
                        level: 0,
                        min_x: length * i as f64,
                        max_x: length * (i + 1) as f64,
                        min_y: length * j as f64,
                        max_y: length * (j + 1) as f64,
                        min_z: length * k as f64,
                        max_z: length * (k + 1) as f64,
                    })
                })
            })
        });
        let mut index = 0;
        while index < tree.len() {
            if let Some(block) = tree[index].homogeneous(&data) {
                tree[index].block = Some(block)
            } else {
                tree.subdivide(index)
            }
            index += 1;
        }
        #[cfg(feature = "profile")]
        println!(
            "           \x1b[1;93m⤷ Octree initialization\x1b[0m {:?} ",
            time.elapsed()
        );
        tree
    }
    fn into_finite_elements(
        self,
        _remove: Option<Vec<u8>>,
        scale: &Vector,
        translate: &Vector,
    ) -> Result<HexahedralFiniteElements, String> {
        #[cfg(feature = "profile")]
        let time = Instant::now();
        let xscale = scale[0];
        let yscale = scale[1];
        let zscale = scale[2];
        let xtranslate = translate[0];
        let ytranslate = translate[1];
        let ztranslate = translate[2];
        if xscale <= 0.0 {
            return Err("Need to specify xscale > 0.0".to_string());
        } else if yscale <= 0.0 {
            return Err("Need to specify yscale > 0.0".to_string());
        } else if zscale <= 0.0 {
            return Err("Need to specify zscale > 0.0".to_string());
        }
        let mut element_node_connectivity = vec![];
        let mut nodal_coordinates = Coordinates::zero(0);
        let mut cells_nodes = vec![0; self.len()];
        let mut node_index = 1;
        self.iter().enumerate().for_each(|(cell_index, cell)| {
            if cell.get_cells().is_none() {
                cells_nodes[cell_index] = node_index;
                nodal_coordinates.0.append(&mut vec![Coordinate::new([
                    0.5 * (cell.get_min_x() + cell.get_max_x()) * xscale + xtranslate,
                    0.5 * (cell.get_min_y() + cell.get_max_y()) * yscale + ytranslate,
                    0.5 * (cell.get_min_z() + cell.get_max_z()) * zscale + ztranslate,
                ])]);
                node_index += 1;
            }
        });
        let mut connected_faces = [None; 6];
        let mut d_01_subcells = None;
        let mut d_04_subcells = None;
        let mut d_14_subcells = None;
        let mut d014_subcells = None;
        let mut fa_0_subcells = [0; NUM_OCTANTS];
        let mut fa_1_subcells = [0; NUM_OCTANTS];
        let mut fa_4_subcells = [0; NUM_OCTANTS];
        let mut face_0_faces = &[None; NUM_FACES];
        self.iter().for_each(|cell| {
            if let Some(cell_subcells) = cell.get_cells() {
                if cell_subcells
                    .iter()
                    .filter(|&&subcell| self[subcell].get_cells().is_none())
                    .count()
                    == NUM_OCTANTS
                {
                    element_node_connectivity.push([
                        cells_nodes[cell_subcells[0]],
                        cells_nodes[cell_subcells[1]],
                        cells_nodes[cell_subcells[3]],
                        cells_nodes[cell_subcells[2]],
                        cells_nodes[cell_subcells[4]],
                        cells_nodes[cell_subcells[5]],
                        cells_nodes[cell_subcells[7]],
                        cells_nodes[cell_subcells[6]],
                    ]);
                    connected_faces = [None; 6];
                    d_01_subcells = None;
                    d_04_subcells = None;
                    d_14_subcells = None;
                    d014_subcells = None;
                    cell.get_faces()
                        .iter()
                        .enumerate()
                        .for_each(|(face_index, face_cell)| {
                            if let Some(face_cell_index) = face_cell {
                                if let Some(face_subcells) = self[*face_cell_index].get_cells() {
                                    if face_subcells
                                        .iter()
                                        .filter(|&&subcell| self[subcell].get_cells().is_none())
                                        .count()
                                        == NUM_OCTANTS
                                    {
                                        match face_index {
                                            0 => {
                                                element_node_connectivity.push([
                                                    cells_nodes[face_subcells[2]],
                                                    cells_nodes[face_subcells[3]],
                                                    cells_nodes[cell_subcells[1]],
                                                    cells_nodes[cell_subcells[0]],
                                                    cells_nodes[face_subcells[6]],
                                                    cells_nodes[face_subcells[7]],
                                                    cells_nodes[cell_subcells[5]],
                                                    cells_nodes[cell_subcells[4]],
                                                ]);
                                                connected_faces[0] = Some(face_cell_index)
                                            }
                                            1 => {
                                                element_node_connectivity.push([
                                                    cells_nodes[cell_subcells[1]],
                                                    cells_nodes[face_subcells[0]],
                                                    cells_nodes[face_subcells[2]],
                                                    cells_nodes[cell_subcells[3]],
                                                    cells_nodes[cell_subcells[5]],
                                                    cells_nodes[face_subcells[4]],
                                                    cells_nodes[face_subcells[6]],
                                                    cells_nodes[cell_subcells[7]],
                                                ]);
                                                connected_faces[1] = Some(face_cell_index)
                                            }
                                            4 => {
                                                element_node_connectivity.push([
                                                    cells_nodes[face_subcells[4]],
                                                    cells_nodes[face_subcells[5]],
                                                    cells_nodes[face_subcells[7]],
                                                    cells_nodes[face_subcells[6]],
                                                    cells_nodes[cell_subcells[0]],
                                                    cells_nodes[cell_subcells[1]],
                                                    cells_nodes[cell_subcells[3]],
                                                    cells_nodes[cell_subcells[2]],
                                                ]);
                                                connected_faces[4] = Some(face_cell_index)
                                            }
                                            2 | 3 | 5 => {}
                                            _ => panic!(),
                                        }
                                    }
                                }
                            }
                        });
                    if let Some(face_4) = connected_faces[4] {
                        fa_4_subcells = self[*face_4].get_cells().unwrap();
                    }
                    if let Some(face_1) = connected_faces[1] {
                        fa_1_subcells = self[*face_1].get_cells().unwrap();
                        if connected_faces[4].is_some() {
                            if let Some(diag_subcells) =
                                self[self[*face_1].get_faces()[4].unwrap()].get_cells()
                            {
                                if diag_subcells
                                    .iter()
                                    .filter(|&&subcell| self[subcell].get_cells().is_none())
                                    .count()
                                    == NUM_OCTANTS
                                {
                                    d_14_subcells = Some(diag_subcells);
                                }
                            }
                        }
                    }
                    if let Some(face_0) = connected_faces[0] {
                        fa_0_subcells = self[*face_0].get_cells().unwrap();
                        face_0_faces = self[*face_0].get_faces();
                        if connected_faces[1].is_some() {
                            if let Some(diag_subcells) = self[face_0_faces[1].unwrap()].get_cells()
                            {
                                if diag_subcells
                                    .iter()
                                    .filter(|&&subcell| self[subcell].get_cells().is_none())
                                    .count()
                                    == NUM_OCTANTS
                                {
                                    d_01_subcells = Some(diag_subcells);
                                }
                            }
                        }
                        if connected_faces[4].is_some() {
                            if let Some(diag_subcells) = self[face_0_faces[4].unwrap()].get_cells()
                            {
                                if diag_subcells
                                    .iter()
                                    .filter(|&&subcell| self[subcell].get_cells().is_none())
                                    .count()
                                    == NUM_OCTANTS
                                {
                                    d_04_subcells = Some(diag_subcells);
                                    if d_01_subcells.is_some() && d_01_subcells.is_some() {
                                        if let Some(diag_subcells) = self
                                            [self[face_0_faces[1].unwrap()].get_faces()[4].unwrap()]
                                        .get_cells()
                                        {
                                            if diag_subcells
                                                .iter()
                                                .filter(|&&subcell| {
                                                    self[subcell].get_cells().is_none()
                                                })
                                                .count()
                                                == NUM_OCTANTS
                                            {
                                                d014_subcells = Some(diag_subcells)
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                    if let Some(diag_subcells) = d_01_subcells {
                        element_node_connectivity.push([
                            cells_nodes[fa_0_subcells[3]],
                            cells_nodes[diag_subcells[2]],
                            cells_nodes[fa_1_subcells[0]],
                            cells_nodes[cell_subcells[1]],
                            cells_nodes[fa_0_subcells[7]],
                            cells_nodes[diag_subcells[6]],
                            cells_nodes[fa_1_subcells[4]],
                            cells_nodes[cell_subcells[5]],
                        ]);
                    }
                    if let Some(diag_subcells) = d_04_subcells {
                        element_node_connectivity.push([
                            cells_nodes[diag_subcells[6]],
                            cells_nodes[diag_subcells[7]],
                            cells_nodes[fa_4_subcells[5]],
                            cells_nodes[fa_4_subcells[4]],
                            cells_nodes[fa_0_subcells[2]],
                            cells_nodes[fa_0_subcells[3]],
                            cells_nodes[cell_subcells[1]],
                            cells_nodes[cell_subcells[0]],
                        ]);
                    }
                    if let Some(d_14_subcells) = d_14_subcells {
                        element_node_connectivity.push([
                            cells_nodes[fa_4_subcells[5]],
                            cells_nodes[d_14_subcells[4]],
                            cells_nodes[d_14_subcells[6]],
                            cells_nodes[fa_4_subcells[7]],
                            cells_nodes[cell_subcells[1]],
                            cells_nodes[fa_1_subcells[0]],
                            cells_nodes[fa_1_subcells[2]],
                            cells_nodes[cell_subcells[3]],
                        ]);
                        if let Some(diag_subcells) = d014_subcells {
                            element_node_connectivity.push([
                                cells_nodes[d_04_subcells.unwrap()[7]],
                                cells_nodes[diag_subcells[6]],
                                cells_nodes[d_14_subcells[4]],
                                cells_nodes[fa_4_subcells[5]],
                                cells_nodes[fa_0_subcells[3]],
                                cells_nodes[d_01_subcells.unwrap()[2]],
                                cells_nodes[fa_1_subcells[0]],
                                cells_nodes[cell_subcells[1]],
                            ]);
                        }
                    }
                }
            }
        });
        let fem = Ok(HexahedralFiniteElements::from_data(
            vec![1; element_node_connectivity.len()],
            element_node_connectivity,
            nodal_coordinates,
        ));
        #[cfg(feature = "profile")]
        println!(
            "           \x1b[1;93m  Dualization of primal\x1b[0m {:?} ",
            time.elapsed()
        );
        fem
    }
    fn octree_into_finite_elements(
        self,
        remove: Option<Vec<u8>>,
        scale: &Vector,
        translate: &Vector,
    ) -> Result<HexahedralFiniteElements, String> {
        let xscale = scale[0];
        let yscale = scale[1];
        let zscale = scale[2];
        let xtranslate = translate[0];
        let ytranslate = translate[1];
        let ztranslate = translate[2];
        if xscale <= 0.0 {
            return Err("Need to specify xscale > 0.0".to_string());
        } else if yscale <= 0.0 {
            return Err("Need to specify yscale > 0.0".to_string());
        } else if zscale <= 0.0 {
            return Err("Need to specify zscale > 0.0".to_string());
        }
        let mut removed_data = remove.unwrap_or_default();
        removed_data.sort();
        removed_data.dedup();
        let num_elements = self
            .iter()
            .filter(|cell| removed_data.binary_search(&cell.get_block()).is_err())
            .count();
        let mut element_blocks = vec![0; num_elements];
        let mut element_node_connectivity = vec![from_fn(|_| 0); num_elements];
        let mut nodal_coordinates: Coordinates = (0..num_elements * NUM_NODES_HEX)
            .map(|_| Coordinate::zero())
            .collect();
        let mut index = 0;
        self.iter()
            .filter(|cell| removed_data.binary_search(&cell.get_block()).is_err())
            .zip(
                element_blocks
                    .iter_mut()
                    .zip(element_node_connectivity.iter_mut()),
            )
            .for_each(|(cell, (block, connectivity))| {
                *block = cell.get_block() as usize;
                *connectivity = from_fn(|n| n + index + NODE_NUMBERING_OFFSET);
                nodal_coordinates[index] = Coordinate::new([
                    cell.get_min_x().copy() * xscale + xtranslate,
                    cell.get_min_y().copy() * yscale + ytranslate,
                    cell.get_min_z().copy() * zscale + ztranslate,
                ]);
                nodal_coordinates[index + 1] = Coordinate::new([
                    cell.get_max_x().copy() * xscale + xtranslate,
                    cell.get_min_y().copy() * yscale + ytranslate,
                    cell.get_min_z().copy() * zscale + ztranslate,
                ]);
                nodal_coordinates[index + 2] = Coordinate::new([
                    cell.get_max_x().copy() * xscale + xtranslate,
                    cell.get_max_y().copy() * yscale + ytranslate,
                    cell.get_min_z().copy() * zscale + ztranslate,
                ]);
                nodal_coordinates[index + 3] = Coordinate::new([
                    cell.get_min_x().copy() * xscale + xtranslate,
                    cell.get_max_y().copy() * yscale + ytranslate,
                    cell.get_min_z().copy() * zscale + ztranslate,
                ]);
                nodal_coordinates[index + 4] = Coordinate::new([
                    cell.get_min_x().copy() * xscale + xtranslate,
                    cell.get_min_y().copy() * yscale + ytranslate,
                    cell.get_max_z().copy() * zscale + ztranslate,
                ]);
                nodal_coordinates[index + 5] = Coordinate::new([
                    cell.get_max_x().copy() * xscale + xtranslate,
                    cell.get_min_y().copy() * yscale + ytranslate,
                    cell.get_max_z().copy() * zscale + ztranslate,
                ]);
                nodal_coordinates[index + 6] = Coordinate::new([
                    cell.get_max_x().copy() * xscale + xtranslate,
                    cell.get_max_y().copy() * yscale + ytranslate,
                    cell.get_max_z().copy() * zscale + ztranslate,
                ]);
                nodal_coordinates[index + 7] = Coordinate::new([
                    cell.get_min_x().copy() * xscale + xtranslate,
                    cell.get_max_y().copy() * yscale + ytranslate,
                    cell.get_max_z().copy() * zscale + ztranslate,
                ]);
                index += NUM_NODES_HEX;
            });
        Ok(HexahedralFiniteElements::from_data(
            element_blocks,
            element_node_connectivity,
            nodal_coordinates,
        ))
    }
    fn pair(&mut self) {
        #[cfg(feature = "profile")]
        let time = Instant::now();
        let mut block = 0;
        let mut index = 0;
        let mut subsubcells: Vec<bool>;
        while index < self.len() {
            if let Some(subcells) = self[index].cells {
                subsubcells = subcells
                    .into_iter()
                    .map(|subcell| self[subcell].cells.is_some())
                    .collect();
                if subsubcells.iter().any(|&subsubcell| subsubcell)
                    && !subsubcells.iter().all(|&subsubcell| subsubcell)
                {
                    subcells
                        .into_iter()
                        .filter(|&subcell| self[subcell].cells.is_none())
                        .collect::<Vec<usize>>()
                        .into_iter()
                        .for_each(|subcell| {
                            block = self[subcell].get_block();
                            self.subdivide(subcell);
                            self.iter_mut()
                                .rev()
                                .take(NUM_OCTANTS)
                                .for_each(|cell| cell.block = Some(block))
                        })
                }
            }
            index += 1;
        }
        #[cfg(feature = "profile")]
        println!(
            "           \x1b[1;93m  Pairing hanging nodes\x1b[0m {:?} ",
            time.elapsed()
        );
    }
    fn prune(&mut self) {
        #[cfg(feature = "profile")]
        let time = Instant::now();
        self.retain(|cell| cell.cells.is_none());
        #[cfg(feature = "profile")]
        println!(
            "             \x1b[1;93mPruning of the octree\x1b[0m {:?} ",
            time.elapsed()
        );
    }
    fn subdivide(&mut self, index: usize) {
        let new_indices = from_fn(|n| self.len() + n);
        let mut new_cells = self[index].subdivide(new_indices);
        self[index]
            .get_faces()
            .clone()
            .iter()
            .enumerate()
            .for_each(|(face, face_cell)| {
                if let Some(neighbor) = face_cell {
                    if let Some(kids) = self[*neighbor].cells {
                        match face {
                            0 => {
                                new_cells[0].faces[0] = Some(kids[2]);
                                new_cells[1].faces[0] = Some(kids[3]);
                                new_cells[4].faces[0] = Some(kids[6]);
                                new_cells[5].faces[0] = Some(kids[7]);
                                self[kids[2]].faces[2] = Some(new_indices[0]);
                                self[kids[3]].faces[2] = Some(new_indices[1]);
                                self[kids[6]].faces[2] = Some(new_indices[4]);
                                self[kids[7]].faces[2] = Some(new_indices[5]);
                            }
                            1 => {
                                new_cells[1].faces[1] = Some(kids[0]);
                                new_cells[3].faces[1] = Some(kids[2]);
                                new_cells[5].faces[1] = Some(kids[4]);
                                new_cells[7].faces[1] = Some(kids[6]);
                                self[kids[0]].faces[3] = Some(new_indices[1]);
                                self[kids[2]].faces[3] = Some(new_indices[3]);
                                self[kids[4]].faces[3] = Some(new_indices[5]);
                                self[kids[6]].faces[3] = Some(new_indices[7]);
                            }
                            2 => {
                                new_cells[2].faces[2] = Some(kids[0]);
                                new_cells[3].faces[2] = Some(kids[1]);
                                new_cells[6].faces[2] = Some(kids[4]);
                                new_cells[7].faces[2] = Some(kids[5]);
                                self[kids[0]].faces[0] = Some(new_indices[2]);
                                self[kids[1]].faces[0] = Some(new_indices[3]);
                                self[kids[4]].faces[0] = Some(new_indices[6]);
                                self[kids[5]].faces[0] = Some(new_indices[7]);
                            }
                            3 => {
                                new_cells[0].faces[3] = Some(kids[1]);
                                new_cells[2].faces[3] = Some(kids[3]);
                                new_cells[4].faces[3] = Some(kids[5]);
                                new_cells[6].faces[3] = Some(kids[7]);
                                self[kids[1]].faces[1] = Some(new_indices[0]);
                                self[kids[3]].faces[1] = Some(new_indices[2]);
                                self[kids[5]].faces[1] = Some(new_indices[4]);
                                self[kids[7]].faces[1] = Some(new_indices[6]);
                            }
                            4 => {
                                new_cells[0].faces[4] = Some(kids[4]);
                                new_cells[1].faces[4] = Some(kids[5]);
                                new_cells[2].faces[4] = Some(kids[6]);
                                new_cells[3].faces[4] = Some(kids[7]);
                                self[kids[4]].faces[5] = Some(new_indices[0]);
                                self[kids[5]].faces[5] = Some(new_indices[1]);
                                self[kids[6]].faces[5] = Some(new_indices[2]);
                                self[kids[7]].faces[5] = Some(new_indices[3]);
                            }
                            5 => {
                                new_cells[4].faces[5] = Some(kids[0]);
                                new_cells[5].faces[5] = Some(kids[1]);
                                new_cells[6].faces[5] = Some(kids[2]);
                                new_cells[7].faces[5] = Some(kids[3]);
                                self[kids[0]].faces[4] = Some(new_indices[4]);
                                self[kids[1]].faces[4] = Some(new_indices[5]);
                                self[kids[2]].faces[4] = Some(new_indices[6]);
                                self[kids[3]].faces[4] = Some(new_indices[7]);
                            }
                            _ => panic!(),
                        }
                    }
                }
            });
        self.extend(new_cells);
    }
}
