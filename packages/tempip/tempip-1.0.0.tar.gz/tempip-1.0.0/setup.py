
from setuptools import setup, find_packages

setup(
    name='tempip',        
    version='1.0.0',     
    packages=find_packages(),
    install_requires=[''],
    entry_points={
        'console_scripts': [
            'tempip-cli=tempip.cli:main', 
        ],
    },
)
