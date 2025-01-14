# setup.py

from setuptools import setup, find_packages

setup(
    name="speck_cipher",
    version="0.1.0",
    packages=find_packages(),
    description="Speck cipher implementation in Python",
    author="Azaliya",
    author_email="azakhabi19@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
