#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

# Default requirements if requirements.txt is not found
default_requirements = ["numpy<2", "matplotlib", "pyautogui", "requests", "retry"]

# Try to read requirements.txt, fall back to default if not found
try:
    with open("requirements.txt") as f:
        install_requirements = f.read().splitlines()
except FileNotFoundError:
    install_requirements = default_requirements

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
    keywords="t_screenwise",
    name="t_screenwise",
    packages=find_packages(include=["t_screenwise", "t_screenwise.*"]),
    test_suite="tests",
    url="https://www.thoughtful.ai/",
    version="1.0.1",
    zip_safe=False,
    install_requires=install_requirements,
    package_data={
        "": ["requirements.txt"],
    },
    include_package_data=True,
)
