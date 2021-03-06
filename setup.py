#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup  # type: ignore


setup(
    name='pyipasnhistory',
    version='2.2-dev',
    author='Raphaël Vinot',
    author_email='raphael.vinot@circl.lu',
    maintainer='Raphaël Vinot',
    url='https://github.com/D4-project/IPASN-History/client',
    description='Python client for IP ASN History',
    packages=['pyipasnhistory'],
    scripts=['bin/ipasn.py'],
    install_requires=['requests'],
    classifiers=[
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Operating System :: POSIX :: Linux',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Telecommunications Industry',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python :: 3',
        'Topic :: Security',
        'Topic :: Internet',
    ]
)
