import setuptools
import os

with open("README.rst", "r", encoding="utf-8") as f:
    long_description = f.read()


with open(os.path.join("cable_robo_mount", "version.py")) as f:
    txt = f.read()
    last_line = txt.splitlines()[-1]
    version_string = last_line.split()[-1]
    version = version_string.strip("\"'")


setuptools.setup(
    name="cable_robo_mount",
    version=version,
    description="Simulating a segmented imaging reflector",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Spyridon Daglas, Sebastian Achim Mueller",
    author_email="spirosdag@gmail.com",
    url="https://github.com/cherenkov-plenoscope/cable_robo_mount",
    packages=[
        "cable_robo_mount",
        "cable_robo_mount.plot",
        "cable_robo_mount.plot.non_flat",
        "cable_robo_mount.camera",
        "cable_robo_mount.tension_ring",
        "cable_robo_mount.mirror_alignment",
        "cable_robo_mount.SAP2000_bridge",
        "cable_robo_mount.mctracer_bridge",
        "cable_robo_mount.tools",
        "cable_robo_mount.tools.non_flat",
    ],
    package_data={"cable_robo_mount": []},
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Astronomy",
    ],
)
