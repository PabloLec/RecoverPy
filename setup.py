from re import findall
from subprocess import check_output

from setuptools import setup, find_packages


with open("requirements.txt", "r") as req_fp:
    required_packages = req_fp.readlines()

# Use README for long description
with open("README.md", "r") as readme_fp:
    long_description = readme_fp.read()

def get_version():
    last_tag = str(check_output("git tag --list | tail -1", shell=True))
    last_version = re.findall("([0-9]+\.[0-9]+\.[0-9]+", last_tag)
    
    return last_version

try:
    last_version = get_version()
except:
    last_version = "1.1.0"
    
setup(
    name="recoverpy",
    version=last_version,
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
        "Development Status :: 5 - Production/Stable",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
