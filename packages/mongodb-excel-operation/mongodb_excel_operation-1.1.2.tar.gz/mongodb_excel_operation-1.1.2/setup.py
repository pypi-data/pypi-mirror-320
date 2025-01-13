from setuptools import setup, find_packages

setup(
    name="mongodb_excel_operation",  # Replace with your package name
    version="1.1.2",  # Replace with your version
    description="mongo_excel_operations.py is a Python utility module designed to facilitate seamless operations between MongoDB and Excel files. This module provides functions to import data from Excel files into MongoDB collections, export data from MongoDB collections into Excel files, read files (CSV or Excel) into Pandas DataFrames with proper data type handling, and manage MongoDB indexes on collections.",
    long_description= '',
    long_description_content_type="text/markdown",
    author="Prasanna J",
    author_email="Prasanna24@gmail.com",
    url="https://github.com/PrasannaJK8/mongo-excel-operation",  # Replace with your repo URL
    packages=find_packages(),
    install_requires=[],  # Add any dependencies here
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Replace with your license
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
