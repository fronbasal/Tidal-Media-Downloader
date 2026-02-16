#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""Setup file for backward compatibility with older pip/setuptools versions."""

from setuptools import setup, find_packages

# Read version from package
__version__ = "2025.12.1"

setup(
    name='tidal-dl',
    version=__version__,
    license="Apache-2.0",
    description="Download music and videos from Tidal (Refactored)",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",

    author='Yaronzz',
    author_email="yaronhuang@foxmail.com",

    url="https://github.com/fronbasal/Tidal-Media-Downloader",

    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    include_package_data=True,

    python_requires='>=3.8',

    install_requires=[
        "requests>=2.32"
        "pycryptodome>=3.9.0"
        "pydub>=0.25.1"
        "prettytable>=3.16.0"
        "mutagen>=1.47.0"
        "colorama>=0.4.6"
        "certifi=>2025.10.5"
        "pycparser>=2.23"
    ],

    entry_points={
        'console_scripts': [
            'tidal-dl=tidal_dl.main:main',
        ]
    },

    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Sound/Audio",
    ],
)
