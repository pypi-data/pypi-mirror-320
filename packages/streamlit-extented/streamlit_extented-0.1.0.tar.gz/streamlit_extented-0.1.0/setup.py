from setuptools import setup, find_packages

setup(
    name="streamlit-extented",  
    version="0.1.0",  
    author="Voronov Andrey",  
    description="Расширение для работы с базами данных через pyodbc с поддержкой JSON",
    long_description=open("README.md",encoding="utf-8").read(), 
    long_description_content_type="text/markdown", 
    packages=find_packages(),  
    install_requires=[
        "pyodbc", 
    ],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7", 
)

