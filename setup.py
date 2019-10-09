import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(name='reflector_study',
    version='0.0.1',
    description='Simulating a segmented imaging reflector',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Spyridon Daglas, Sebastian Achim Mueller',
    author_email='spirosdag@gmail.com',
    url='',
    license='GPL v3',
    packages=['reflector_study'],
    install_requires=[],
    zip_safe=False,
)
