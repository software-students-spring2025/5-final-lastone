# setup.py
from setuptools import setup, find_packages

setup(
    name="app",
    version="0.1",
    packages=find_packages(),
    package_dir={"": "app/src"},
)