# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('tsc_web_api/version.txt', 'r') as f:
    version = f.read().strip()
with open('readme.md', 'r') as f:
    long_description = f.read()
with open('requirements.in', 'r') as f:
    requirements = f.read().strip().split('\n')

setup(
    name='tsc_web_api',
    version=version,
    description="tsc_web_api",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='aitsc',
    license='GPLv3',
    url='https://github.com/aitsc/tsc_web_api',
    keywords='tools',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries',
    ],
    install_requires=requirements,
    python_requires='>=3.9',
)
