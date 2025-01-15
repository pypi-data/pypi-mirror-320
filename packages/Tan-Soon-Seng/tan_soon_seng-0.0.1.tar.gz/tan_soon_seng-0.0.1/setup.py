# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

__version__ = "0.0.1"

# The main interface is through Pybind11Extension.
# * You can add cxx_std=11/14/17, and then build_ext can be removed.
# * You can set include_pybind11=false to add the include directory yourself,
#   say from a submodule.
#
# Note:
#   Sort input source files if you glob sources to ensure bit-for-bit
#   reproducible builds (https://github.com/pybind/python_example/pull/53)

ext_modules = [
    Pybind11Extension(
        "Tan_Soon_Seng",
        ["src/main.cpp"],
        # Example: passing in the version to the compiled code
        define_macros=[("VERSION_INFO", __version__)],
    ),
]

with open("README.md") as f:
    Readme = f.read()

setup(
    name="Tan_Soon_Seng",
    version=__version__,
    author="Kwong Ye Kun",
    author_email="23006148@siswa.um.edu.my",
    description="C++ code packaged for use in Python for KIG2013 Assignment",
    long_description=Readme,
    long_description_content_type="text/markdown",
    license="MIT",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.7",
)
