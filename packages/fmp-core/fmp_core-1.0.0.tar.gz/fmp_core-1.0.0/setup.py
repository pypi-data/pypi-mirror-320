import tomllib

from setuptools import find_packages, setup


def get_version() -> str:
    with open("pyproject.toml", "rb") as f:
        pyproject = tomllib.load(f)
        return pyproject["tool"]["poetry"]["version"]


setup(
    name="fmp-core",
    version=get_version(),
    packages=find_packages(),
    install_requires=[
        "pydantic",
        "pydantic-settings",
        "motor",
    ],
    author="bartnyk",
    author_email="jakub@bartnyk.pl",
    description="Core package for stock predictor",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/bartnyk/fmp-core",
    python_requires=">=3.12",
)
