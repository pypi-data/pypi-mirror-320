from setuptools import setup, find_packages

setup(
    name="streamlit-mssql",  
    version="0.1.1", 
    description="Streamlit integration for MSSQL using pyodbc",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Voronov Andrei",
    packages=find_packages(),
    install_requires=[
        "pyodbc",
        "json"  
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
