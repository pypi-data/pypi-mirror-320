import codecs
import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))


with codecs.open(os.path.join(here, 'README.md'), encoding='utf-8') as fh:
    long_description = '\n' + fh.read()


VERSION = '1.0.1'
DESCRIPTION = '1'
LONG_DESCRIPTION = '1'


setup(
    name='access_diction',
    version=VERSION,
    author='aorphine',
    description=DESCRIPTION,
    long_description_content_type='text/markdown',
    long_description=long_description,
    packages=find_packages(),
    install_requires=[],
    keywords=['dict', 'access_path'],
    classifiers=[],
)

