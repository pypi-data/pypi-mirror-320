import plane_partitions
from plane_partitions import PlanePartition
from pprint import pprint

print(plane_partitions.version())
print()
# NOTE: Height must be passed to the constructor, as it CANNOT be derived from the underlying lists
print(PlanePartition([[0, 0], [0, 0]], 2).sspp_tp_tspp())

print(PlanePartition([[1, 0], [0, 0]], 2).sspp_tp_tspp())

print(PlanePartition([[2, 0], [0, 0]], 2).sspp_tp_tspp())

print(PlanePartition([[2, 1], [0, 0]], 2).sspp_tp_tspp())

print(PlanePartition([[2, 1], [1, 0]], 2).sspp_tp_tspp())

print()

print(PlanePartition([[2, 1], [1, 0]], 2).to_tikz_diagram())

print()

part = PlanePartition([[0,0,0],[0,0,0],[0,0,0]], 3)
pprint(part.rowmotion_orbit())

print()
for i in range(8):
    print(part, part.complement())
    part = part.rowmotion()

print()

pprint([[0, 1],[0,0]])
print("Is Partition:", PlanePartition([[0, 1],[0,0]], 2).is_plane_partition())

print()

part = PlanePartition([[13,13,13,13,13,13,13,11,11,9,9,7,7],
                       [13,13,13,13,13,12,12,10,10,9,7,7,5],
                       [13,13,13,13,13,11,10,10,8,8,6,5,5],
                       [13,13,13,12,12,11,9,9,8,6,6,5,3],
                       [13,13,13,12,10,10,8,7,6,6,4,4,3],
                       [13,12,11,11,10,8,8,7,5,5,4,2,1],
                       [13,12,10,9,8,8,6,6,4,3,2,2,1],
                       [11,10,10,9,7,7,6,4,4,3,1,0,0],
                       [11,10,8,8,6,5,4,4,2,2,1,0,0],
                       [9,9,8,6,6,5,3,3,2,0,0,0,0],
                       [9,7,6,6,4,4,2,1,1,0,0,0,0],
                       [7,7,5,5,4,2,2,0,0,0,0,0,0],
                       [7,5,5,3,3,1,1,0,0,0,0,0,0]], 13)

print("Complement = Rowmotion:", part.complement() == part.rowmotion())
part = PlanePartition([[5,5,5,5,5],[5,5,5,4,4],[3,3,3,2,1],[3,1,0,0,0],[2,0,0,0,0]], 5)
for i in range(part.rowmotion_orbit_length()):
    part = part.rowmotion()
    print(part.to_tikz_diagram())

p0 = PlanePartition([[0, 0], [0, 0]], 2)
p1 = PlanePartition([[1, 0], [0, 0]], 2)
p2 = PlanePartition([[2, 0], [0, 0]], 2)
p3 = PlanePartition([[2, 1], [0, 0]], 2)
p4 = PlanePartition([[2, 1], [1, 0]], 2)

d = {p0: "hi", p1: "there", p2: "this", p3: "is", p4: "hashable"}
for _, v in d.items():
    print(v)

for i in [p0, p1, p2, p3, p4]:
    print(i, i[0,0], i[0,1], i[1,0], i[1,1])
