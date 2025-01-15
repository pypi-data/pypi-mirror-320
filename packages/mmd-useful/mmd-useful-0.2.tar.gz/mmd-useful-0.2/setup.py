from setuptools import setup, find_packages

VERSION = "0.2"  # PEP-440

NAME = "mmd-useful"

with open('README.md', 'r') as f:
    readme = f.read()

INSTALL_REQUIRES = []

setup(
    name=NAME,
    version=VERSION,
    packages=find_packages(),
    INSTALL_REQUIRES=[],
    long_description=readme,
    long_description_content_type='text/markdown'
)