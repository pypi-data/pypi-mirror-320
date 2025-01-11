from setuptools import setup, find_packages

setup(
    name='ensfc-stemm',
    __version__='0.1.1',
    packages=find_packages(),
    install_requires=[
        "sympy"
    ]
)