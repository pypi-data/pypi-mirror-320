import os
import re
import ast
from skbuild import setup

package = 'pyvgrid'
def version():
    _version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", package, "__init__.py")
    _version_re = re.compile(r"\s*__version__\s*=\s*(\"|')(?P<version>\d+\.\d+\.\d+)(\"|')\s*\#*.*")
    with open(_version_file, "r") as f:
        lines = [l.strip() for l in f.readlines() if 'version' in l]
    for l in lines:
        m = _version_re.match(l)
        if m:
            version = m.group('version')

setup(
    name=package,
    version=version(),
    packages=[package, os.path.join(package, 'cli')],
    package_dir={"": "src"},
    cmake_install_dir="src/pyvgrid",
    cmake_minimum_required_version="3.13",
    setup_requires=["scikit-build", "setuptools"],
    include_package_data=False ,
)

