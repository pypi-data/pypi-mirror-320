from setuptools import setup  # type: ignore

setup(
    name="bumimport",
    version="1.0.0",
    description="A Python package for various lazy (discouraged) import strategies.",
    url="https://www.github.com/ryanbaekr/bumimport",
    author="Ryan Baker",
    license="AGPL",
    packages=["bumimport"],
    python_requires=">=3.9",

    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
    ],
)
