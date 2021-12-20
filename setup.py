from setuptools import setup

setup(
    name='OAST Simulator',
    version='0.1',
    description='M/M/c queue simulator',
    author='darkroom2',
    author_email='rkomorowski97@gmail.com',
    install_requires=[
        'numpy',
        'scipy'
    ],
    packages=['simulation']
)
