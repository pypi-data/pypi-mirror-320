# setup.py
from setuptools import setup, find_packages

setup(
    name="safisha",
    version="0.1.7",
    description="Programu ya kusafisha Mac yako.",
    author="Mark Francis",
    author_email="safisha@ngao.pro",
    packages=find_packages(),
    install_requires=[],  # Add dependencies here if needed
    entry_points={
        "console_scripts": [
            "safisha=safisha.cli:main",  # Ensure this is correct
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
    ],
)