from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import sys
with open("README.txt", "r", encoding = "utf-8") as f:
    readme = f.read()
pyminizip_sources = ["src/pyminizip/py_minizip.c", "src/pyminizip/py_miniunz.c", "zlib-1.2.11/contrib/minizip/zip.c", "zlib-1.2.11/contrib/minizip/unzip.c", "zlib-1.2.11/contrib/minizip/ioapi.c", "zlib-1.2.11/adler32.c", "zlib-1.2.11/compress.c", "zlib-1.2.11/crc32.c", "zlib-1.2.11/deflate.c", "zlib-1.2.11/infback.c", "zlib-1.2.11/inffast.c", "zlib-1.2.11/inflate.c", "zlib-1.2.11/inftrees.c", "zlib-1.2.11/trees.c", "zlib-1.2.11/uncompr.c", "zlib-1.2.11/zutil.c"]
if "win32" in sys.platform:
    pyminizip_sources.append("zlib-1.2.11/contrib/minizip/iowin32.c")
pyminizip = Extension(
    name = "pysdk.pyminizip",
    sources = pyminizip_sources,
    include_dirs = ['src/pyminizip','zlib-1.2.11','zlib-1.2.11/contrib/minizip'],
)
c_extensions = [
    pyminizip
]
math_gcd = Extension(
    name = "pysdk.math.gcd",
    sources = ["src/pysdk/math/gcd.cpp"],
    language = "c++"
)
math_prime = Extension(
    name = "pysdk.math.prime",
    sources = ["src/pysdk/math/prime.cpp"],
    language = "c++"
)
cpp_extensions = [
    math_gcd,
    math_prime
]
dict_read = Extension(
    name = "pysdk.dict.read",
    sources = ["src/pysdk/dict/read.pyx"],
)
dict_write = Extension(
    name = "pysdk.dict.write",
    sources = ["src/pysdk/dict/write.pyx"],
)
list_count = Extension(
    name = "pysdk.list.count",
    sources = ["src/pysdk/list/count.pyx"],
)
list_for_each = Extension(
    name = "pysdk.list.for_each",
    sources = ["src/pysdk/list/for_each.pyx"],
)
list_read = Extension(
    name = "pysdk.list.read",
    sources = ["src/pysdk/list/read.pyx"],
)
list_write = Extension(
    name = "pysdk.list.write",
    sources = ["src/pysdk/list/write.pyx"],
)
list_strutils_to_list = Extension(
    name = "pysdk.list.strutils.to_list",
    sources = ["src/pysdk/list/strutils/to_list.pyx"],
)
cython_extensions = [
    dict_read,
    dict_write,
    list_count,
    list_for_each,
    list_read,
    list_write,
    list_strutils_to_list
]
setup(
    name = "pl-python-sdk-full",
    version = "0.5a1",
    description = "Some useful utilities for Python.",
    long_description = readme,
    long_description_content_type = "text/plain",
    license = "GPLv2",
    author = "Pemrilect",
    author_email = "retres243@outlook.com",
    python_requires = ">=3.6",
    package_dir = {"": "src"},
    packages = [package for package in find_packages(where = "src")],
    ext_modules = c_extensions + cpp_extensions + cythonize(cython_extensions),
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: C",
        "Programming Language :: C++",
        "Programming Language :: Cython",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities"
    ]
)
