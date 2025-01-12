
from setuptools import setup, find_packages

setup(
    name='tempip',        
    version='1.0.1',     
    long_description="an program that auto generates basic template, and input as needed",
    packages=find_packages(),
    install_requires=[''],
    entry_points={
        'console_scripts': [
            'tempip-cli=tempip.cli:main', 
        ],
    },
)
