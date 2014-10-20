#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='simtrans',
      version='0.0.1',
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
        'console_scripts': ['simtrans = simtrans.simtrans:main']
      }
)
