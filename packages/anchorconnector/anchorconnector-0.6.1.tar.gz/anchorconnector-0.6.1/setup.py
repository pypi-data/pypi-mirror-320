"""
Anchor Connector for Podcast Data

This package allows you to fetch data from the inofficial Anchor Podcast API.
The API is not documented and may change at any time. Use at your own risk.
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="anchorconnector",
    packages=find_packages(include=["anchorconnector"]),
    version="0.6.1",
    description="Anchor Connector for Podcast Data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Open Podcast",
    license="MIT",
    entry_points={
        "console_scripts": [
            "anchorconnector = anchorconnector.__main__:main",
        ]
    },
    install_requires=["requests", "loguru", "PyYAML", "tenacity", "myst_parser[docs]"],
)
