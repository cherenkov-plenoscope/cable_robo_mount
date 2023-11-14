import numpy as np


def generate_flat_nodes(reflector_ijk):
    joints_ijk = reflector_ijk["joints"]
    geometry = reflector_ijk["geometry"]
    flat_nodes = []
    flat_joints = []

    flat_nodes_indices = -np.ones(
        shape=(
            geometry.lattice_range_i,
            geometry.lattice_range_j,
            geometry.lattice_range_k,
        )
    )

    node_count = 0
    for i, joint_jk in enumerate(joints_ijk):
        for j, joint_k in enumerate(joint_jk):
            for k, joint in enumerate(joint_k):
                if len(joint) > 0:
                    flat_nodes.append(reflector_ijk["nodes"][i, j, k])
                    flat_joints.append(joint)
                    flat_nodes_indices[i, j, k] = node_count
                    node_count += 1

    return {
        "nodes": np.array(flat_nodes),
        "nodes_indices": flat_nodes_indices,
        "joints": flat_joints,
    }


def flatten(reflector_ijk):
    flat = generate_flat_nodes(reflector_ijk)
    flat_nodes_indices = flat["nodes_indices"]

    number_of_bars = reflector_ijk["bars"].shape[0]
    flat_bars = np.zeros(shape=(number_of_bars, 2), dtype=np.int64)
    for i, bar in enumerate(reflector_ijk["bars"]):
        flat_bars[i, 0] = flat_nodes_indices[bar[0][0], bar[0][1], bar[0][2]]
        flat_bars[i, 1] = flat_nodes_indices[bar[1][0], bar[1][1], bar[1][2]]

    number_of_mirror_tripods = reflector_ijk["mirror_tripods"].shape[0]
    flat_mirror_tripods = np.zeros(
        shape=(number_of_mirror_tripods, 3), dtype=np.int64
    )
    for i, tripod in enumerate(reflector_ijk["mirror_tripods"]):
        flat_mirror_tripods[i, 0] = flat_nodes_indices[
            tripod[0][0], tripod[0][1], tripod[0][2]
        ]
        flat_mirror_tripods[i, 1] = flat_nodes_indices[
            tripod[1][0], tripod[1][1], tripod[1][2]
        ]
        flat_mirror_tripods[i, 2] = flat_nodes_indices[
            tripod[2][0], tripod[2][1], tripod[2][2]
        ]

    number_of_fixtures = reflector_ijk["fixtures"].shape[0]
    flat_fixtures = np.zeros(number_of_fixtures, dtype=np.int64)
    for i, fixture in enumerate(reflector_ijk["fixtures"]):
        flat_fixtures[i] = flat_nodes_indices[
            fixture[0], fixture[1], fixture[2]
        ]

    return {
        "nodes": flat["nodes"],
        "joints": flat["joints"],
        "bars": flat_bars,
        "mirror_tripods": flat_mirror_tripods,
        "fixtures": flat_fixtures,
        "geometry": reflector_ijk["geometry"],
    }
