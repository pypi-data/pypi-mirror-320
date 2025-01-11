# setup.py
from setuptools import setup, find_packages

setup(
    name="darshika_test_package",
    version="0.0.3",
    author="Darshika Joshi",
    author_email="joshidarshika88@gmail.com",
    description="A package for Test parameters management",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/darshike-wp/test_package.git",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
