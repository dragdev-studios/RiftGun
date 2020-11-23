from setuptools import setup

from riftgun.cog import __version__

with open('requirements.txt') as f:
    requirements = f.readlines()

setup(
    name='riftgun',
    version=__version__,
    packages=['riftgun'],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url='https://github.com/dragdev-studios/RiftGun',
    license='Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International Public License',
    author='EEKIM10',
    author_email='eek@clicksminuteper.net',
    description='A new module for providing easy remote support with discord bots',
    install_requires=requirements
)
