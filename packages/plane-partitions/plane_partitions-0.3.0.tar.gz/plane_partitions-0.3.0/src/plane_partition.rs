use std::{collections::BTreeSet, usize};

use pyo3::pyclass;

pub mod impls;
pub mod pyfunctions;

/// Struct representing a plane partition.
#[pyclass(eq, hash, frozen)]
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct PlanePartition {
    /// n is the len of data
    pub n: usize,
    /// m is the len of the nested vecs in data
    pub m: usize,
    /// l is the max of the flattened data
    pub l: usize,
    pub data: Vec<Vec<u8>>
}

//#[derive(Debug, Clone, PartialEq, Eq)]
//pub struct PlanePartition {
//    pub len: usize,
//    pub data: Vec<Vec<u8>>,
//}

#[derive(Debug, Default, Clone)]
pub struct PlanePartitonSet(BTreeSet<(u8, u8, u8)>);

pub fn check_point_in_matrix(point: (u8, u8, u8), matrix: &PlanePartition) -> bool {
    return matrix[point.0 as usize][point.1 as usize] > point.2;
}

pub fn s3_one_point(point: (u8, u8, u8)) -> [(u8, u8, u8); 6] {
    let i = point.0;
    let j = point.1;
    let k = point.2;

    [
        (i, j, k),
        (j, k, i),
        (k, i, j),
        (k, j, i),
        (j, i, k),
        (i, k, j),
    ]
}

pub fn matrix_to_set(matrix: &PlanePartition) -> PlanePartitonSet {
    let mut set = PlanePartitonSet::default();
    let len_n = matrix.n;
    let len_m = matrix.m;
    let len_l = matrix.l;

    // We never really use anything more than n=20, and 20^3 = 8000, which really isn't that bad. 
    // 8000 is baby number to big computer.
    for i in 0..len_n {
        for j in 0..len_m {
            for k in 0..len_l {
                set.insert((i as u8, j as u8, k as u8));
            }
        }
    }

    PlanePartitonSet(
        set.into_iter()
            .filter(|x| check_point_in_matrix(*x, &matrix))
            .collect::<BTreeSet<_>>(),
    )
}

pub fn set_to_matrix(set: &PlanePartitonSet, len_n: usize, len_m: usize, len_l: usize) -> PlanePartition {
    let mut matrix = PlanePartition {
        n: len_n,
        m: len_m,
        l: len_l,
        data: vec![vec![0; len_m]; len_m],
    };

    for &(i, j, k) in set.iter() {
        matrix[i as usize][j as usize] = u8::max(matrix[i as usize][j as usize], k + 1)
    }

    matrix
}

pub fn ungravity_matrix(matrix: &PlanePartition) -> PlanePartition {
    let mut mat: Vec<Vec<u8>> = vec![];

    // NOTE: This should still work, it uses the len api
    // should ungravity the matrix
    for x in 0..matrix.len() {
        let mut vec: Vec<u8> = vec![];
        for y in 0..matrix[0].len() {
            if matrix[y][x] == 0 {
                vec.push(0);
            } else {
                vec.push(matrix[x][y] + x as u8 + y as u8);
            };
        }
        for _ in 0..x {
            vec.insert(0, 0);
            let _ = vec.pop();
        }
        mat.push(vec);
    }

    return PlanePartition {
        n: matrix.n,
        m: matrix.m,
        l: matrix.l,
        data: mat,
    };
}

pub fn strongly_stable_to_totally_stable(matrix: &PlanePartition) -> PlanePartition {
    let matrix = ungravity_matrix(matrix);

    let points = matrix_to_set(&matrix);

    let mut set_rep = PlanePartitonSet::default();
    for point in points.into_iter() {
        s3_one_point(point).iter().for_each(|x| {
            set_rep.insert(*x);
        });
    }
    set_to_matrix(&set_rep, matrix.n, matrix.m, matrix.l)
}
