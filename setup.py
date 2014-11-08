#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from simtrans import __version__

setup(name='simtrans',
      version=__version__,
      description='Utility to convert robot simulation model to one another.',
      long_description='Utility to convert robot simulation model to one another.',
      author='',
      author_email='',
      url='',
      license='',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: ',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development',
      ],
      packages=['simtrans',
                'OpenHRP',
                'OpenHRP__POA'],
      entry_points={
          'console_scripts': ['simtrans = simtrans.cli:main']
      },
      test_suite='nose2.collector.collector')
