import os
import setuptools

here = os.path.abspath(os.path.dirname(__file__))

with open("README.md", "r", encoding="UTF-8") as fh:
    long_description = fh.read()

# Get the code version
version = {}
with open(os.path.join(here, "autogen/version.py")) as fp:
    exec(fp.read(), version)
__version__ = version["__version__"]

setuptools.setup(
    name="seed-autogen",
    version=__version__,
    description="Alias package for pyautogen",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["seed_pyautogen==" + __version__],
    url="https://github.com/Seedtech-Club/ag2",
    author="SeedTech",
    author_email="kev1nzh37@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    license="Apache Software License 2.0",
    python_requires=">=3.8,<3.14",
    packages=setuptools.find_packages(include=["autogen", "autogen.*"]),
)
