from setuptools import setup, find_packages
import os

VERSION = os.getenv("PACKAGE_VERSION", "0.0.0")

setup(
    name="tamarix_analytics",
    version='0.0.6',
    description="A Python package for row matching and F1 score calculations.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Tamarix Technologies",
    author_email="kristian@tamarix.tech",
    packages=find_packages(),
    install_requires=[
        "munkres",
        "pydantic",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
