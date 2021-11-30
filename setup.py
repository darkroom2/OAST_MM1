from setuptools import setup

setup(
    name='MPI Simulator',
    version='0.1',
    description='Inverse Erlang Simulator',
    author='darkroom2',
    author_email='rkomorowski97@gmail.com',
    install_requires=[
        'numpy',
        'matplotlib',
        'scipy'
    ],
    packages=['simulator']
)
