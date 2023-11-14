import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="cable_robo_mount",
    version="0.0.1",
    description="Simulating a segmented imaging reflector",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Spyridon Daglas, Sebastian Achim Mueller",
    author_email="spirosdag@gmail.com",
    url="https://github.com/cherenkov-plenoscope/cable_robo_mount",
    packages=["cable_robo_mount"],
    python_requires=">=3",
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
