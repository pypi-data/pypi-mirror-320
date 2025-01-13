"""Lib setup"""

from setuptools import find_packages, setup


def requirements() -> list[str]:
    """Load requirements"""
    with open("requirements.txt") as fileobj:
        return [line.strip() for line in fileobj]


with open("README.md", encoding="utf-8") as fh:
    doc_long_description = fh.read()

setup(
    name="rointe-sdk",
    version="1.6.0",
    author="tggm",
    description="Python SDK for rointeconnect.com",
    long_description=doc_long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tggm/rointe-sdk",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements(),
)
