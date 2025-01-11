from setuptools import find_packages, setup

with open("optinum/README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="optinum",
    version="0.3.1",
    description="A Library For Numerical Methods Computation",
    package_dir={"": "optinum"},
    packages=find_packages(where="optinum"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/galkin-v/optinum",
    author="Galkin Vladimir",
    author_email="galkin.vova1@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    install_requires=["bson >= 0.5.10"],
    extras_require={
        "dev": ["numpy >= 1.21.2", "matplotlib >= 3.4.3"],
    },
    python_requires=">=3.10",
)
