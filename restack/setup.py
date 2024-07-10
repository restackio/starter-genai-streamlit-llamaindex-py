from setuptools import setup, find_packages

setup(
    name="restack",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "temporalio==1.6.0"
    ],
)