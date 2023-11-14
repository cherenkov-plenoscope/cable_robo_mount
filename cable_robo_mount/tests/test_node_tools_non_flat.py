import reflector_study as rs
import numpy as np


def test_node_range_lower_limit():
    nodes = np.zeros(shape=(1, 2, 3, 3))
    assert rs.tools.non_flat.node_in_range(nodes, [0, 0, -1]) == False
    assert rs.tools.non_flat.node_in_range(nodes, [0, -1, 0]) == False
    assert rs.tools.non_flat.node_in_range(nodes, [0, -1, -1]) == False
    assert rs.tools.non_flat.node_in_range(nodes, [-1, 0, 0]) == False
    assert rs.tools.non_flat.node_in_range(nodes, [-1, 0, -1]) == False
    assert rs.tools.non_flat.node_in_range(nodes, [-1, -1, -1]) == False


def test_node_range_each_dimension():
    nodes = np.zeros(shape=(1, 2, 3, 3))
    assert rs.tools.non_flat.node_in_range(nodes, [-1, 0, 0]) == False
    assert rs.tools.non_flat.node_in_range(nodes, [0, 0, 0]) == True
    assert rs.tools.non_flat.node_in_range(nodes, [1, 0, 0]) == False

    assert rs.tools.non_flat.node_in_range(nodes, [0, -1, 0]) == False
    assert rs.tools.non_flat.node_in_range(nodes, [0, 0, 0]) == True
    assert rs.tools.non_flat.node_in_range(nodes, [0, 1, 0]) == True
    assert rs.tools.non_flat.node_in_range(nodes, [0, 2, 0]) == False

    assert rs.tools.non_flat.node_in_range(nodes, [0, 0, -1]) == False
    assert rs.tools.non_flat.node_in_range(nodes, [0, 0, 0]) == True
    assert rs.tools.non_flat.node_in_range(nodes, [0, 0, 1]) == True
    assert rs.tools.non_flat.node_in_range(nodes, [0, 0, 2]) == True
    assert rs.tools.non_flat.node_in_range(nodes, [0, 0, 3]) == False


def test_node_range_upper_limit():
    nodes = np.zeros(shape=(1, 2, 3, 3))
    assert rs.tools.non_flat.node_in_range(nodes, [0, 0, 3]) == False
    assert rs.tools.non_flat.node_in_range(nodes, [0, 2, 0]) == False
    assert rs.tools.non_flat.node_in_range(nodes, [0, 2, 3]) == False
    assert rs.tools.non_flat.node_in_range(nodes, [1, 0, 0]) == False
    assert rs.tools.non_flat.node_in_range(nodes, [1, 0, 3]) == False
    assert rs.tools.non_flat.node_in_range(nodes, [1, 2, 3]) == False


def test_node_positions():
    nodes = np.zeros(shape=(2, 2, 2, 3))
    nodes[0, 0, 0] = np.array([4.2, 1.3, 3.7])

    np.testing.assert_array_equal(
        rs.tools.non_flat.node_position(nodes, [0, 0, 0]),
        np.array([4.2, 1.3, 3.7]),
    )

    nodes[0, 1, 0] = np.array([3.2, 1.0, -1.2])

    np.testing.assert_array_equal(
        rs.tools.non_flat.node_position(nodes, [0, 1, 0]),
        np.array([3.2, 1.0, -1.2]),
    )

    np.testing.assert_array_equal(
        rs.tools.non_flat.node_position(nodes, [1, 0, 0]), np.zeros(3)
    )
