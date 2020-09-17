import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ernie",
    version="0.1.0",
    author="Thomas Kreuzer",
    author_email="thomas.kreuzer@rwth-aachen.de",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/finkler/ernie",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=["matplotlib", "numpy"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    scripts=["bin/ernie"],
)
