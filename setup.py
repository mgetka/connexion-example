# pylint: disable=missing-module-docstring,invalid-name
import os
from textwrap import dedent

from setuptools import find_packages, setup

with open("requirements.txt", "r") as f:
    requirements = list(
        filter(lambda line: not line.startswith("--"), f.read().splitlines())
    )

try:
    with open("requirements-dev.txt", "r") as f:
        requirements_dev = list(
            filter(lambda line: not line.startswith("--"), f.read().splitlines())
        )
except FileNotFoundError:
    requirements_dev = []

with open("VERSION", "r") as f:
    version = f.read().strip()

with open("src/conexample/version.py", "w") as f:
    f.write(
        dedent(
            """\
            # pylint: disable=missing-docstring
            __version__ = "{version}"
            """.format(
                version=version
            )
        )
    )

setup(
    name="conexample",
    version=version,
    description="Example connexion application.",
    author="Michał Getka",
    author_email="michal.getka@gmail.pl",
    url="https://github.com/mgetka/connexion-example",
    python_requires=">=3.7",
    include_package_data=True,
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={"conexample": ["*.env"], "conexample.api.rest": ["*.yml"],},
    install_requires=requirements,
    extras_require={"dev": requirements_dev},
    entry_points="""
        [console_scripts]
        conexample-dev=conexample.entrypoint:run_dev
    """,
)
