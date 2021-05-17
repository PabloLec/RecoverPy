from setuptools import setup, find_packages

with open("requirements.txt", "r") as req_fp:
    required_packages = req_fp.readlines()

# Use README for long description
with open("README.md", "r") as readme_fp:
    long_description = readme_fp.read()

setup(
    name="recoverpy",
    version="1.0.5",
    author="Pablo Lecolinet",
    author_email="pablolec@pm.me",
    description="A command line interface for recovering overwritten or deleted text data.",
    license="GNU GPLv3",
    keywords="data recovery cui",
    url="https://github.com/pablolec/recoverpy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests", "docs"]),
    entry_points={
        "console_scripts": [
            "recoverpy = recoverpy:main",
        ],
    },
    install_requires=required_packages,
    package_data={"recoverpy": ["recoverpy/config.yaml"]},
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
