# setup.py
from setuptools import setup, find_packages
import os

lib_folder = os.path.dirname(os.path.realpath(__file__))
requirement_path = f"{lib_folder}/requirements.txt"
install_requires = []
if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        install_requires = f.read().splitlines()

version = "0.0.0-default"
versions_file = f"{lib_folder}/docai-dev/VERSION"
if os.path.isfile(versions_file):
    with open(versions_file) as f:
        version = f.read().strip()
        print(version)

setup(
    name='docailite',
    version=version,
    description='DocAI Lite Python module',
    author='Sonu Sudhakaran',
    author_email='sonu.sudhakaran@gmail.com',
    packages=find_packages(),
    install_requires=install_requires,  # List any dependencies here
)
