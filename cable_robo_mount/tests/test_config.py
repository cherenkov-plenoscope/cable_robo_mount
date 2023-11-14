import cable_robo_mount as rs
import tempfile
import os


def test_default_config():
    initial_config = {
        "optics": {
            "focal_length": 75.0,
            "davies_cotton_over_parabola_ratio": 0.0,
            "max_outer_radius": 25.0,
        },
        "space_frame": {
            "material": {
                "yielding_point": 1337.0,
            },
            "bar": {
                "outer_diameter": 0.05,
                "thickness": 0.001,
            },
            "mirror_facet_weight": {
                "surface_weight": 25.0,
                "actuator_weight": 5.0,
            },
        },
    }

    with tempfile.TemporaryDirectory() as temp_path:
        config_path = os.path.join(temp_path, "test_config.json")
        rs.config.write(initial_config, config_path)
        read_config = rs.config.read(config_path)

        assert initial_config == read_config
