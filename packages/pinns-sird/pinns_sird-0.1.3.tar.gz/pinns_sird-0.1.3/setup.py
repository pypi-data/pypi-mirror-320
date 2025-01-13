from setuptools import setup, find_packages

setup(
    name='pinns_sird',
    version='0.1.3',
    description='A Python package for solving SIRD models using PINNs.',
    long_description='Long description goes here...',
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'torch',
        'pandas',
        'matplotlib',
        'scipy',
    ],
    include_package_data=True,  # Include additional files specified
    package_data={
        'pinns_sird': ['data/*'],  # Include all files in the data/ directory
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)