#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup, find_packages

setup(
    name="pygbop",
    version="0.2.2.4",
    author="huang.xiaogang",
    author_email="huang.xiaogang@geely.com",
    description="Geely GBOP Client",
    long_description=open("readme.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://pypi.python.org/pypi/GbopApiClient",
    packages=find_packages(exclude=["*.*"]),
    include_package_data=True,
    py_modules=[],
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Utilities",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
