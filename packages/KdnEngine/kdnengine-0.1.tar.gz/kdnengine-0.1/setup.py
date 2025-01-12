from setuptools import setup, find_packages
from pathlib import Path

setup(
    name="KdnEngine",
    version="0.1",
    description="A simple game engine for 3D games",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/KdntNinja/KdnEngine",
    author="KdntNinja",
    project_urls={"Source": "https://github.com/KdntNinja/KdnEngine"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10,<3.13",
    install_requires=[
        "PyOpenGL",
        "pybullet",
        "pynput",
    ],
    packages=find_packages(),
    include_package_data=True,
)
