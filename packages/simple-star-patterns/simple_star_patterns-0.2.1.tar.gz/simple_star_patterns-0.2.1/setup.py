# setup.py

from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="simple-star-patterns",
    version="0.2.1",
    author="Yash Agrawal",
    author_email="yashmtr1744@gmail.com",
    description="A simple library for printing star patterns",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["simple_star_patterns"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)