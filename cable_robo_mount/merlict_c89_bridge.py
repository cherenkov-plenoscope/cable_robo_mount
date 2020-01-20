import numpy
import json

def angle_between(v1, v2):
    return np.arccos(np.dot(v1, v2)/(
        np.linalg.norm(v1)*
        np.linalg.norm(v2)))

def list_f8(l):
    return [float(l[0]), float(l[1]), float(l[2])]


def cylinder(
    start_pos,
    end_pos,
    radius,
    surface={"inner": 0, "outer": 1},
    user_id=1,
):
    rotsym_axis = end_pos - start_pos;
    length = np.linalg.norm(rotsym_axis)
    assert(length >= 0)
    position = start_pos + rotsym_axis/2.0;

    ez = np.array([0, 0, 1])
    theta = angle_between(rotsym_axis, ez)
    if theta == 0.:
        axis = ez
        angle = 0.
    else:
        axis = np.cross(rotsym_axis, ez)
        angle = -theta

    return {
      "type": "Cylinder",
      "id": int(user_id),
      "pos": list_f8(position),
      "rot": {
        "repr": "axis_angle",
        "axis": list_f8(axis),
        "angle": float(angle)},
      "radius": float(radius),
      "length": float(length),
      "surface": surface
    }


def bars_to_merlictC89(nodes, bars, bar_radius, surface):
    bar_dicts = []
    for i, bar in enumerate(bars):
            start_pos = nodes[bar[0]]
            end_pos = nodes[bar[1]]
            bar_dicts.append(
                cylinder(
                    user_id=i+1,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    radius=bar_radius,
                    surface=surface))
    return bar_dicts


def reflector_to_scenery(reflector, bar_radius=0.05):
    sc = {}
    sc["functions"] = [
        [
            [200e-9, 0.0],
            [1200e-9, 0.0]
        ],
        [
            [200e-9, 1.0],
            [1200e-9, 1.0]
        ],
    ]
    sc["colors"] = [
        [22, 9, 255],
        [255, 91, 49],
    ]
    sc["surfaces"] = [
        {
          "material": 100,
          "medium_refraction": 1,
          "medium_absorbtion": 0,
          "boundary_layer_specular_reflection": 0,
          "boundary_layer_diffuse_reflection": 1,
          "color": 0
        },
        {
          "material": 100,
          "medium_refraction": 1,
          "medium_absorbtion": 0,
          "boundary_layer_specular_reflection": 0,
          "boundary_layer_diffuse_reflection": 1,
          "color": 1
        }
    ]
    sc["children"] = [
        {
            "type": "Frame",
            "id": 133337,
            "pos": [0, 0, 1],
            "rot": {"repr": "tait_bryan", "xyz": [0, 0, 0]},
            "children" :  bars_to_merlictC89(
                nodes=reflector["nodes"],
                bars=reflector["bars"],
                bar_radius=bar_radius,
                surface={"inner": 0, "outer": 1})
        }
    ]
    return sc

def write_reflector(reflector, path, bar_radius=0.05):
    refl_dict = reflector_to_scenery(reflector=reflector, bar_radius=bar_radius)
    with open(path, "wt") as f:
        f.write(json.dumps(refl_dict))
