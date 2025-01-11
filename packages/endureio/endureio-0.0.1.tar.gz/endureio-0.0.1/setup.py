import builtins
from distutils.core import setup

import setuptools


def setup_package():
    setup(
        name="endureio",
        version="0.0.1",
        author="PySport",
        author_email="info@pysport.org",
        url="https://pysport.org/",
        packages=setuptools.find_packages(exclude=["tests"]),
        license="TBD",
        description="",
        long_description="",
        long_description_content_type="text/markdown",
        classifiers=[
            "Intended Audience :: Developers",
            "Intended Audience :: Science/Research",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "License :: OSI Approved",
            "Topic :: Scientific/Engineering",
        ],
    )


if __name__ == "__main__":
    setup_package()

