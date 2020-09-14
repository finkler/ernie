import setuptools

setuptools.setup(
    name="ernie",
    version="0.1",
    license="MIT",
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
