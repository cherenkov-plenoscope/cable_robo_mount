import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as plt_Polygon
from . import optical_geometry

HEXA = np.array([1.0, 0.0, 0.0])
HEXB = np.array([0.5, np.sqrt(3.0)/2.0, 0.0])


def init_mesh():
    return {"vertices": {}, "bars": {}, "faces": {}, "vertex_normals":{}}


def make_hexagonal_mesh_in_xy_plane(radial_steps):
    # vertices
    # ========
    n = radial_steps
    mesh = init_mesh()
    for dA in np.arange(-n, n+1, 1):
        for dB in np.arange(-n, n+1, 1):

            bound_upper = -dA + n
            bound_lower = -dA - n
            if dB <= bound_upper and dB >= bound_lower:
                mesh["vertices"][(dA, dB)] = dA * HEXA + dB * HEXB

    # faces
    # =====
    for dA in np.arange(-n, n+1, 1):
        for dB in np.arange(-n, n+1, 1):

            # top face
            # --------
            top_face_verts = [(dA, dB), (dA+1, dB), (dA, dB+1)]

            all_faces_in_mesh = True
            for top_face_vert in top_face_verts:
                if top_face_vert not in mesh["vertices"]:
                    all_faces_in_mesh = False

            if all_faces_in_mesh:
                mesh["faces"][(dA, dB, 1)] = {"vertices": list(top_face_verts)}
            # bottom face
            # -----------
            bottom_face_verts = [(dA, dB), (dA+1, dB), (dA+1, dB-1)]

            all_faces_in_mesh = True
            for bottom_face_vert in bottom_face_verts:
                if bottom_face_vert not in mesh["vertices"]:
                    all_faces_in_mesh = False

            if all_faces_in_mesh:
                mesh["faces"][(dA, dB, -1)] = {"vertices": list(bottom_face_verts)}

    return mesh


def make_spherical_hex_cap(outer_hex_radius, curvature_radius, num_steps=10):
    # flat 2d-mesh
    m = make_hexagonal_mesh_in_xy_plane(radial_steps=num_steps)

    # scale
    for vkey in m["vertices"]:
        m["vertices"][vkey] *= 2.0 * outer_hex_radius * 1.0/num_steps

    # elevate z-axis
    for vkey in m["vertices"]:
        distance_to_z_axis = np.hypot(
            m["vertices"][vkey][0], m["vertices"][vkey][1]
        )
        m["vertices"][vkey][2] = optical_geometry.z_sphere(
            distance_to_z_axis=distance_to_z_axis,
            curvature_radius=curvature_radius
        )

    # vertex-normals
    # --------------
    center_of_curvature = np.array([0.0, 0.0, curvature_radius])
    for vkey in m["vertices"]:
        diff = center_of_curvature - m["vertices"][vkey]
        normal = diff / np.linalg.norm(diff)
        vnkey = (vkey[0], vkey[1], "c")
        m["vertex_normals"][vnkey] = normal

    for fkey in m["faces"]:
        m["faces"][fkey]["vertex_normals"] = []
        for vi in range(3):
            vkey = m["faces"][fkey]["vertices"][vi]
            vnkey = (vkey[0], vkey[1], "c")
            m["faces"][fkey]["vertex_normals"].append(vnkey)

    return m



def _add_face(ax, vertices, alpha=None, color="blue"):
    p = plt_Polygon(vertices, closed=False, facecolor=color, alpha=alpha)
    ax.add_patch(p)


def plot_mesh(mesh):
    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    ax.set_aspect("equal")
    for vkey in mesh["vertices"]:
        ax.plot(mesh["vertices"][vkey][0], mesh["vertices"][vkey][1], "xb")

    for fkey in mesh["faces"]:
        vs = []
        for ii in range(3):
            vkey = mesh["faces"][fkey]["vertices"][ii]
            vs.append(mesh["vertices"][vkey][0:2])
        vs = np.array(vs)
        _add_face(ax=ax, vertices=vs, alpha=0.5, color="green")
    plt.show()



def flatten_mesh(construction_mesh):
    cmesh = construction_mesh
    v_dict = {}
    for vi, vkey in enumerate(cmesh["vertices"]):
        v_dict[vkey] = vi
    vn_dict = {}
    for vni, vnkey in enumerate(cmesh["vertex_normals"]):
        vn_dict[vnkey] = vni

    obj = {
        "v": [],
        "vn": [],
        "f": [],
    }

    for vkey in cmesh["vertices"]:
        obj["v"].append(cmesh["vertices"][vkey])
    for vnkey in cmesh["vertex_normals"]:
        obj["vn"].append(cmesh["vertex_normals"][vnkey])

    for fkey in cmesh["faces"]:
        vs = []
        for dim in range(3):
            vs.append(v_dict[cmesh["faces"][fkey]["vertices"][dim]])
        vns = []
        for dim in range(3):
            vns.append(vn_dict[cmesh["faces"][fkey]["vertex_normals"][dim]])
        obj["f"].append({"v": vs, "vn": vns})
    return obj


def mesh_to_wavefront(obj):
    # COUNTING STARTS AT ONE
    s = []
    s.append("# vertices")
    for v in obj["v"]:
        s.append("v {:f} {:f} {:f}".format(v[0], v[1], v[2]))
    s.append("# vertex-normals")
    for vn in obj["vn"]:
        s.append("vn {:f} {:f} {:f}".format(vn[0], vn[1], vn[2]))
    s.append("# faces")
    for f in obj["f"]:
        s.append("f {:d}//{:d} {:d}//{:d} {:d}//{:d}".format(
                1 + f["v"][0], 1 + f["vn"][0],
                1 + f["v"][1], 1 + f["vn"][1],
                1 + f["v"][2], 1 + f["vn"][1],
            )
        )
    return "\n".join(s)


def write_obj(path, obj):
    with open(path, "wt") as fout:
        fout.write(mesh_to_wavefront(obj=obj))
