# setup.py
from setuptools import setup, find_packages

setup(
    name="baseconnect",
    version="0.133",
    description="Database connection library for SQL Server",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Domiter Dominik",
    author_email="dominik.domiter@autowallis.hu",
    url="https://github.com/Domiterd/BaseConnect",
    packages=find_packages(),
    install_requires=[
        "pyodbc",
        "pandas",
    ],
)
