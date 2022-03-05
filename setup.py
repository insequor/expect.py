#!/usr/bin/env python3

import os

from setuptools import setup  # type: ignore


rootdir = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(rootdir, "README.md")) as in_file:
    long_description = in_file.read()

setup(
    name="expect-py",
    version='0.1',
    description="customization over oktest package",
    author='Ozgur Yuksel',
    author_email="ozgur@insequor.com",
    maintainer="Ozgur Yuksel",
    maintainer_email="ozgur@insequor.com",
    packages=["expect"],
    install_requires=["oktest"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT License",
    platforms=["any"],
    python_requires=">=3.8",
    classifiers=[
        "License :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
