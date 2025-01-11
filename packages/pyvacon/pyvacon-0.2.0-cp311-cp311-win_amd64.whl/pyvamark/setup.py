import os
import setuptools
import platform
from setuptools.dist import Distribution

current_dir = os.path.dirname(os.path.realpath(__file__))


class BinaryDistribution(Distribution):
    """Distribution which always forces a binary package with platform name"""

    def has_ext_modules(foo):
        return True


exec(open(current_dir + "/version.py").read())

if platform.system() == "Windows":
    _package_data = {"pyvamark": ["_pyvamark_swig.pyd"]}
else:
    _package_data = {"pyvamark": ["_pyvamark_swig.so"]}

setuptools.setup(
    name="pyvamark",
    version=__version__,
    description="frontmark derivatives pricing python package",
    # long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/frontmark/",
    keywords="",
    # url='https://www.frontmark.de',
    author="frontmark team",
    author_email="info@frontmark.de",
    license="LICENSE",
    license_files=["LICENSE"],
    packages=setuptools.find_packages(),
    package_data=_package_data,
    distclass=BinaryDistribution,
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: C++",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.6",
)
