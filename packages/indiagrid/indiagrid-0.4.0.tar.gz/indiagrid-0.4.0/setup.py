from setuptools import setup, find_packages

__version__ = "0.4.0"
__author__ = "G Kiran"
__license__ = "GPLv2"

# Setup for pip installation
setup(
    name="digipin",
    version=__version__,
    author=__author__,
    author_email="goki75@gmail.com",
    description="A Python library to convert WGS84 latitude and longitude coordinates to the Indian Grid System and vice versa.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/goki75/indiagrid",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.1',
)
