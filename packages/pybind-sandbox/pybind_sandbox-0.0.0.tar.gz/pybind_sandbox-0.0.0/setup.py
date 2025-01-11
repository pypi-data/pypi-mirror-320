import os
import re
import subprocess
import sys
from pathlib import Path

from setuptools import Extension, find_packages, setup
from setuptools.command.build_ext import build_ext


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):

    def build_extension(self, ext):

        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))

        build_temp = os.path.join(self.build_temp, ext.name)
        if not os.path.exists(build_temp):
            os.makedirs(build_temp)

        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
            f"-DPYTHON_EXECUTABLE={sys.executable}"
        ]

        subprocess.check_call(["cmake", ext.sourcedir] + cmake_args, cwd=build_temp)
        subprocess.check_call(["cmake", "--build", "."], cwd=build_temp)

setup(
    name="pybind_sandbox",
    author="PyPartMC team (see https://github.com/open-atmos/PyPartMC/graphs/contributors)",
    author_email="nriemer@illinois.edu",
    description="Python interface to PartMC",
    packages=find_packages(include=["pybind_sandbox"]),
    ext_modules=[CMakeExtension("_pybind_sandbox", "..")],
    cmdclass={"build_ext": CMakeBuild},
    zip_safe=False,
    python_requires=">=3.7",
    setup_requires=["setuptools_scm"],
    install_requires=["numpy"],
    license="GPL-3.0",
    # project_urls={
    #     "Tracker": "https://github.com/open-atmos/PyPartMC/issues",
    #     "Documentation": "https://open-atmos.github.io/PyPartMC",
    #     "Source": "https://github.com/open-atmos/PyPartMC/",
    # },
    # extras_require={
    #     "tests": [
    #         "pytest",
    #         "pytest-order",
    #         "fastcore!=1.5.8",  # https://github.com/fastai/fastcore/issues/439
    #         "ghapi",
    #         "scipy",
    #     ]
    # },
)