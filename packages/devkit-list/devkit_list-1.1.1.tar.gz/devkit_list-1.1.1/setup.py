from setuptools import setup, find_packages
import codecs
setup(
    name = "devkit-list",
    version = "1.1.1",
    description = "Some useful list tools.",
    long_description = codecs.open("README.txt", encoding = "utf-8").read(),
    long_description_content_type = "text/plain",
    author = "Pemrilect",
    author_email = "retres243@outlook.com",
    python_requires = ">=3.10",
    license = "GPLv3",
    packages = find_packages(),
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
