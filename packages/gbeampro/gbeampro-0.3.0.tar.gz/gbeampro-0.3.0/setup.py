from codecs import open

from setuptools import find_packages, setup

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="gbeampro",
    version='0.3.0',
    packages=find_packages(),

    author='Akihiko Shimura',
    author_email='akhksh@gmail.com',
    url='https://github.com/akihiko-shimura/gbeampro',
    description='Python package for designing gaussian laser beam propagation and transformation.',
    long_description=long_description,
    long_description_content_type='text/markdown',

    install_requires=['numpy', 
                      'matplotlib',
                      'ndispers'],

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
)
