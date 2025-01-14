"""Packaging utility for CMCC DDSAPI"""


# https://packaging.python.org/tutorials/packaging-projects/
# https://packaging.python.org/discussions/install-requires-vs-requirements/
# https://pypi.org/classifiers/
# https://setuptools.readthedocs.io/en/latest/setuptools.html

# Run this file with the command:
# $ python setup.py install


import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="ddsapi",
    version="0.6b5",
    author="CMCC Data Delivery System Team",
    author_email="dds-support@cmcc.it",
    description=(
        "Python Client to access and download data from CMCC Data Delivery"
        " System (DDS)"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CMCC-Foundation/ddsapi-client/",
    packages=setuptools.find_packages(),
    install_requires=[
       "geokube==0.2.7.1"
        #"netCDF4>=1.5.3",
        #"scipy>=1.5.2",
        #"requests>=2.23.0",
        #"xarray==2022.10.0",
        #"numpy==1.26.0"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Topic :: Scientific/Engineering :: Hydrology",
    ],
    python_requires=">=3.7",
    license="Apache License, Version 2.0",
)
