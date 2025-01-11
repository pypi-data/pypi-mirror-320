
from setuptools import setup, find_packages

setup(
    name="auto_package_installer",  # Package name on PyPI
    version="0.1.0",    # Version number
    author="Slurrps Mcgee",
    author_email="your.email@example.com",
    description="A package to auto install requirements.txt file",
    # long_description=open("README.md").read(),
    # long_description_content_type="text/markdown",
    url="",  # Project URL
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.13",
)
