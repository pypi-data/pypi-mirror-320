"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2022.
All rights reserved.

Setup script
"""

import os
from itertools import chain

from setuptools import find_namespace_packages, setup

commit_tag = os.environ.get("CI_COMMIT_TAG", "")
if commit_tag.startswith("v"):
    version = commit_tag[1:]
else:
    job_id = os.environ.get("CI_JOB_ID", 0)
    version = f"0.0rc{job_id}+test"

# Here we specify the dependencies of optional packages in parityos_addons.
extras_require = {
    "cirq": ["cirq-core"],
    "qiskit": ["qiskit"],
    "spinz": ["sympy"],
}
# The option [all] will install all optional dependencies.
extras_require["all"] = list(set(chain(*extras_require.values())))
extras_require["dev"] = [
    "basedpyright",
    "numpy",
    "pytest",
    "qiskit-aer",
    "ruff",
    *extras_require["all"],
]

setup(
    name="parityos",
    version=version,
    description="Python bindings to the ParityOS API",
    url="https://parityqc.com/",
    license_files=("License.txt",),
    packages=find_namespace_packages(exclude=["*.test*", "docs*"]),
    package_data={"parityos_addons.documentation.html": ["**/*"]},
    install_requires=[
        "attrs",
        "cattrs",
        "pytest",
        "requests",
        "symengine",
        "typing_extensions>=4.10.0",
    ],
    extras_require=extras_require,
    python_requires=">=3.9",
)
