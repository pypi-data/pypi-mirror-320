#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

install_requirements = open("requirements.txt").readlines()

setup(
    author="Nikolas Cohn, Alejandro Muñoz",
    author_email="support@thoughtful.ai",
    python_requires=">=3.9",
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    description="A Python package for detecting and interacting with screen elements using computer vision and OCR.",
    long_description_content_type="text/markdown",
    long_description=readme,
    keywords="t_screenwise  ",
    name="t_screenwise",
    packages=find_packages(include=["t_screenwise", "t_screenwise.*"]),
    test_suite="tests",
    url="https://www.thoughtful.ai/",
    version="1.0.0",
    zip_safe=False,
    install_requires=install_requirements,
)
