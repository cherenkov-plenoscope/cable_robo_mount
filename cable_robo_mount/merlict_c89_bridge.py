import numpy
import json


def angle_between(v1, v2):
    return np.arccos(
        np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    )


def list_f8(l):
    return [float(l[0]), float(l[1]), float(l[2])]


def cylinder(
    start_pos,
    end_pos,
    radius,
    surface={"inner": 0, "outer": 1},
    user_id=1,
):
    rotsym_axis = end_pos - start_pos
    length = np.linalg.norm(rotsym_axis)
    assert length >= 0
    rotsym_axis = rotsym_axis / length
    position = (start_pos + end_pos) / 2.0

    ez = np.array([0, 0, 1])
    theta = angle_between(rotsym_axis, ez)
    if theta == 0.0:
        axis = ez
        angle = 0.0
    else:
        axis = np.cross(rotsym_axis, ez)
        angle = -theta

    return {
        "type": "Cylinder",
        "id": int(user_id),
        "pos": list_f8(start_pos),
        "rot": {
            "repr": "axis_angle",
            "axis": list_f8(axis),
            "angle": float(angle),
        },
        "radius": float(radius),
        "length": float(length),
        "surface": surface,
    }


def bars_to_merlictC89(nodes, bars, bar_radius, surface):
    bar_dicts = []
    for i, bar in enumerate(bars):
        start_pos = nodes[bar[0]]
        end_pos = nodes[bar[1]]
        bar_dicts.append(
            cylinder(
                user_id=i + 1,
                start_pos=start_pos,
                end_pos=end_pos,
                radius=bar_radius,
                surface=surface,
            )
        )
    return bar_dicts


def reflector_to_scenery(reflector, bar_radius=0.05):
    sc = {}
    sc["functions"] = [
        {"name": "unity", "values": [[200e-9, 1.0], [1200e-9, 1.0]]},
        {
            "name": "refraction_glass",
            "values": [[200e-9, 1.49], [1200e-9, 1.49]],
        },
        {"name": "+infinity", "values": [[200e-9, 9e99], [1200e-9, 9e99]]},
        {"name": "zero", "values": [[200e-9, 0.0], [1200e-9, 0.0]]},
    ]
    sc["colors"] = [
        {"rgb": [22, 9, 255], "name": "blue"},
        {"rgb": [255, 91, 49], "name": "red"},
        {"rgb": [16, 255, 0], "name": "green"},
        {"rgb": [23, 23, 23], "name": "grey"},
    ]
    sc["media"] = [
        {"name": "vacuum", "refraction": "unity", "absorbtion": "+infinity"},
        {
            "name": "glass",
            "refraction": "refraction_glass",
            "absorbtion": "+infinity",
        },
    ]
    sc["default_medium"] = "vacuum"
    sc["surfaces"] = [
        {
            "name": "glass_blue",
            "material": "Transparent",
            "specular_reflection": "unity",
            "diffuse_reflection": "unity",
            "color": "blue",
        },
        {
            "name": "glass_red",
            "material": "Transparent",
            "specular_reflection": "unity",
            "diffuse_reflection": "unity",
            "color": "red",
        },
        {
            "name": "specular_mirror",
            "material": "Phong",
            "specular_reflection": "unity",
            "diffuse_reflection": "zero",
            "color": "green",
        },
        {
            "name": "perfect_absorber",
            "material": "Phong",
            "specular_reflection": "zero",
            "diffuse_reflection": "zero",
            "color": "grey",
        },
    ]
    sc["children"] = [
        {
            "type": "Frame",
            "id": 133337,
            "pos": [0, 0, 1],
            "rot": {"repr": "tait_bryan", "xyz": [0, 0, 0]},
            "children": bars_to_merlictC89(
                nodes=reflector["nodes"],
                bars=reflector["bars"],
                bar_radius=bar_radius,
                surface={
                    "inner": {"medium": "glass", "surface": "glass_blue"},
                    "outer": {
                        "medium": "vacuum",
                        "surface": "specular_mirror",
                    },
                },
            ),
        }
    ]
    return sc


def write_reflector(reflector, path, bar_radius=0.05):
    refl_dict = reflector_to_scenery(
        reflector=reflector, bar_radius=bar_radius
    )
    with open(path, "wt") as f:
        f.write(json.dumps(refl_dict))
