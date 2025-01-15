import pathlib
from setuptools import find_packages, setup

from hestia_earth.config.version import VERSION

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name='hestia_earth_config',
    version=VERSION,
    description="HESTIA's default engine configuration files.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/hestia-earth/hestia-engine-config",
    author="HESTIA Team",
    author_email="guillaume@hestia.earth",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.6",
    ],
    packages=find_packages(exclude=("tests", "scripts")),
    include_package_data=True,
)
