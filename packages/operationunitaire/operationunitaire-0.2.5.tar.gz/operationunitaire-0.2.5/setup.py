from setuptools import setup, find_packages

setup(
    name="operationunitaire",
    version="0.2.4",  # Update version to match your latest release
    description="A Python package for rigorous distillation simulations.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="TASSAOUI Anas",
    author_email="anass.tassaoui@gmail.com",
    url="https://github.com/anastassaoui/operationunitaire",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy>=1.18",
        "pandas>=1.0",
        "scipy>=1.5",
        "tabulate>=0.8",
        "setuptools>=40.0",  # Add setuptools as a dependency
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
