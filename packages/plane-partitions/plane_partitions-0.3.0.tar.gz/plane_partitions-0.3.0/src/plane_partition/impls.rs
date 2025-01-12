use std::{
    collections::BTreeSet,
    fmt::Display,
    ops::{Deref, DerefMut},
};

use itertools::Itertools;

use super::{PlanePartition, PlanePartitonSet};

impl Display for PlanePartition {
    #[allow(unstable_name_collisions)]
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let mut part: String = String::new();

        for row in self.iter() {
            part.push_str(
                &format!(
                    "{{{}}},",
                    row.iter()
                        .filter_map(|x| {
                            if *x != 0 {
                                Some(format!("{x}"))
                            } else {
                                None
                            }
                        })
                        .intersperse(",".to_string())
                        .collect::<String>()
                )[..],
            );
        }

        part.pop();

        write!(
            f,
            "{}\n{}{{{}}}\n{}",
            "\\begin{tikzpicture}", "\\planepartition", part, "\\end{tikzpicture}"
        )
    }
}

impl Deref for PlanePartition {
    type Target = Vec<Vec<u8>>;

    fn deref(&self) -> &Self::Target {
        &self.data
    }
}

impl DerefMut for PlanePartition {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.data
    }
}

impl Deref for PlanePartitonSet {
    type Target = BTreeSet<(u8, u8, u8)>;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl PlanePartitonSet {
    pub fn into_iter(self) -> std::collections::btree_set::IntoIter<(u8, u8, u8)> {
        self.0.into_iter()
    }
}

impl PlanePartition {
    pub fn into_iter(self) -> std::vec::IntoIter<Vec<u8>> {
        self.data.into_iter()
    }
}

impl DerefMut for PlanePartitonSet {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.0
    }
}
