"""
Setup file for producing a PIP package
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="eo-metadata-tools-cmr",
    version="0.0.1",
    author="Thomas Cherry",
    author_email="thomas.a.cherry@nasa.gov",
    description="A python wrapper to the CMR interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nasa/eo-metadata-tools/",
    packages=setuptools.find_packages(exclude=['test']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Apache License 2.0",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.4',
)
