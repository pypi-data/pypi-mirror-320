use pyo3::pymethods;
use itertools::Itertools;

use super::PlanePartition;
use super::*;

#[pymethods]
impl PlanePartition {
    /// The dimensions of the matrix determine the dimensions that plane partition sits on, but the
    /// height determines the height that the blocks can grow to
    #[new]
    fn new(matrix: Vec<Vec<u8>>, height: usize) -> Self {
        PlanePartition {
            n: matrix.len(),
            m: matrix[0].len(),
            l: height,
            data: matrix
        }
    }

    fn __repr__(&self) -> String {
        format!("{:?}", self.data)
    }

    fn __str__(&self) -> String {
        format!("{:?}", self.data)
    }

    fn __getitem__(&self, index: (usize, usize)) -> u8 {
        let (n, m) = index;
        self[n][m]
    }

    // TODO: All the plane partition methods
    fn sspp_tp_tspp(&self) -> Self {
        strongly_stable_to_totally_stable(self)
    }

    fn to_tikz_diagram(&self) -> String {
        format!("{self}")
    }

    fn rowmotion(&self) -> Self {
        let len_n = self.n;
        let len_m = self.m;
        let len_l = self.l;

        let mut ret = PlanePartition {
            n: len_n,
            m: len_m,
            l: len_l,
            data: vec![vec![0; len_n]; len_n]
        };

        let poss_min_not_in = self
            .clone()
            .into_iter()
            .map(|row| row.into_iter().map(|x| (x + 1).clamp(0, len_l as u8)).collect_vec())
            .collect_vec();

        let min_not_in = poss_min_not_in.into_iter().enumerate().map(|(i, row)| {
            row.into_iter().enumerate().map(move |(j, elem)| {
                let left = if j == 0 { u8::MAX } else { self[i][j - 1] };
                let otop = if i == 0 { u8::MAX } else { self[i - 1][j] };
                if elem == self[i][j] {
                    0
                } else if elem <= left && elem <= otop {
                    elem
                } else {
                    0
                }
            }).collect_vec()
        }).collect_vec();


        for i in (0..len_n).rev() {
            let mut min = 0;
            for j in (0..len_m).rev() {
                min = min.max(min_not_in[i][j]);
                ret[i][j] = min;
            }
        }

        for j in (0..len_n).rev() {
            let mut min = 0;
            for i in (0..len_m).rev() {
                min = min.max(min_not_in[i][j]).max(ret[i][j]);
                ret[i][j] = min;
            }
        }

        ret
}

    fn cardinality(&self) -> usize {
        self.iter()
            .flatten()
            .map(|&x| x as usize)
            .sum::<usize>()
    }

    fn rowmotion_orbit_length(&self) -> usize {
        let mut curr = self.rowmotion();
        let mut count = 1;
        while curr != *self {
            count += 1;
            curr = curr.rowmotion();
        }
        count
    }

    fn rowmotion_orbit(&self) -> Vec<Self> {
        let mut orbit = vec![];
        orbit.push(self.clone());
        let mut curr = self.rowmotion();
        while curr != *self {
            orbit.push(curr.clone());
            curr = curr.rowmotion();
        }
        orbit
    }

    fn is_plane_partition(&self) -> bool {
        for i in 0..self.n {
            for j in 0..self.m-1 {
                if self[i][j] < self[i][j+1] {
                    return false;
                }
            }
        }

        for j in 0..self.n {
            for i in 0..self.m-1 {
                if self[i][j] < self[i+1][j] {
                    return false;
                }
            }
        }

        true
    }

    fn complement(&self) -> PlanePartition {
        let len_n = self.n;
        let len_m = self.m;
        let len_l = self.l;

        let mut complement: PlanePartition = PlanePartition {
            n: len_n,
            m: len_m,
            l: len_l,
            data: vec![vec![len_l as u8; len_m]; len_n],
        };

        for i in (0..len_n).rev() {
            for j in (0..len_m).rev() {
                complement[i][j] = complement[i][j] - self[len_n - 1 - i][len_m - 1 - j];
            }
        }

        complement
    }
}
