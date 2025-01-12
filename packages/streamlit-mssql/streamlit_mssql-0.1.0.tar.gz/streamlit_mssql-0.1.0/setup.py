from setuptools import setup, find_packages

setup(
    name="streamlit-mssql",  
    version="0.1.0",  
    description="Библиотека позволяет быстро выполнять запросы к БД, а также превращать данные в JSON",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown', 
    author="Ivanov", 
    packages=find_packages(),  
    install_requires=[  
        "pyodbc",  
    ],
    classifiers=[  
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',  
)
