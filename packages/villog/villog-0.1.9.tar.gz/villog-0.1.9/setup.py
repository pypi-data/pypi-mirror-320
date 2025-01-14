'''setup'''

from pathlib import Path
from setuptools import setup, find_packages

def parse_requirements(filename):
    requirements_path = Path(__file__).parent / filename
    with requirements_path.open() as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(
    name = "villog",
    version = "0.1.9",
    description = "A simple python utility tool for your everyday projects.",
    author = "Krisztián Villers",
    packages = find_packages(),
    long_description = long_description,
    long_description_content_type = "text/markdown",
    install_requires=parse_requirements("requirements.txt"),
)