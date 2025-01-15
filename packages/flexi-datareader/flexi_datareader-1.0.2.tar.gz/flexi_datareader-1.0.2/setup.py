from setuptools import setup, find_packages

setup(
    name="flexi_datareader",  # Name of the package (must be unique in PyPI)
    version="1.0.2",  # Package version
    description="A versatile library for reading datasets from multiple formats and generating synthetic datasets.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",  # Content type for PyPI
    author="Yousof Ghalenoei", 
    author_email="yousof.ghalenoei2017@gmail.com",  
    url="https://github.com/YousofLHC/flexi_datareader",  # URL of your project
    packages=find_packages(),  # Automatically find all packages
    install_requires=[
        "pandas>=1.0",
        "numpy>=1.18",
        "scipy>=1.4",
        "scikit-learn>=0.24"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires=">=3.6",  # Minimum required Python version
)
