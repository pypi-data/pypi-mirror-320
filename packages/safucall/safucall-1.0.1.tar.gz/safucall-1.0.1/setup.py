from setuptools import setup
from pathlib import Path

# Get the directory where setup.py is located
here = Path(__file__).parent

try:
    with open(here / 'requirements.txt') as f:
        required = f.read().splitlines()
except FileNotFoundError:
    required = ['web3>=7.0.0,<8.0.0']

setup(
    install_requires=required
)