from setuptools import setup, Extension
factor = Extension(
    name = "factor",
    sources = ["factor.cpp"],
    language = "c++"
)
gcd = Extension(
    name = "gcd",
    sources = ["gcd.cpp"],
    language = "c++"
)
prime = Extension(
    name = "prime",
    sources = ["prime.cpp"],
    language = "c++"
)
setup(
    name = "devkit-math",
    version = "1.5.2",
    author = "Pemrilect",
    author_email = "retres243@outlook.com",
    license = "MIT",
    python_requires = ">=3.7",
    ext_modules = [factor, gcd, prime],
    classifiers = [
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: C++",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: CPython"
    ]
)
