from setuptools import setup, find_packages
from ivoryos_client.version import __version__ as client_version

setup(
    name='ivoryos-client',  # Name of your package
    version=client_version,  # Version number
    author='Ivory Zhang',
    author_email='ivoryzhang@chem.ubc.ca',
    description='A dynamic client script for generating Python APIs for interacting with SDLs via IvoryOS server',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://gitlab.com/heingroup/ivoryos-client',  # Project URL
    packages=find_packages(),  # Automatically find and include all packages
    install_requires=[
        'requests',  # List all dependencies required by your package
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Minimum version requirement of the Python interpreter
    entry_points={
        'console_scripts': [
            'ivoryos-client=ivoryos_client.client:main',  # Enables running from the command line
        ],
    },
)
