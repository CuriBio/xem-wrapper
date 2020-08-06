# -*- coding: utf-8 -*-
"""Setup configuration."""
from setuptools import find_packages
from setuptools import setup


setup(
    name="xem_wrapper",
    version="0.1",
    description="Functions for interacting with a XEM device",
    url="https://github.com/CuriBio/xem-wrapper",
    author="Curi Bio",
    author_email="contact@curibio.com",
    license="MIT",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=["stdlib_utils>=0.1.20"],
)
