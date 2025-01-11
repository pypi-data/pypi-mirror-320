from setuptools import setup, find_packages

setup(
    name='ensfc-stemm',
    version='0.1.5',
    packages=find_packages(),
    install_requires=[
        "sympy"
    ],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)