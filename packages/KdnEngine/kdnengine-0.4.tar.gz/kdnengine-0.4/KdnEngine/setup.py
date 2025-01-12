from setuptools import setup, find_packages

setup(
    name="KdnEngine",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "PyOpenGL",
        "pybullet",
    ],
)
