from setuptools import setup, find_packages

with open(r"README.md", "r") as file:
    long_description = file.read()

setup(
    name="extdict",
    version="1.0.0",
    packages=find_packages(),
    description=(
        "A Python package for managing tables with content,"
        + " read-only indices, and size constraints."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=r"https://github.com/RinkyDinkyNooble/extdict",
    author="RinkyDinkyNooble",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Topic :: Utilities"
    ],
    extras_require={
        "dev": [
            "pytest>=8.3.4",
            "setuptools>=75.6.0",
            "wheel>=0.45.1",
            "twine>=6.0.1"
        ]
    },
    python_requires=">=3.13.1"
)