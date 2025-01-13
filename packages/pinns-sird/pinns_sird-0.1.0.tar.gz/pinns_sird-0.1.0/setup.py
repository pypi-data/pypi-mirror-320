from setuptools import setup, find_packages

setup(
    name='pinns_sird',
    version='0.1.0',
    description='A Python package for SIRD modeling using PINNs.',
    author='LXA',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'torch',
        'pandas',
        'matplotlib',
        'scipy',
    ],
    entry_points={
        'console_scripts': [
            'run-sird=pinns_sird:run_sird',
        ],
    },
)