#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages, Extension
import versioneer
import subprocess

versioneer.VCS = 'git'
versioneer.versionfile_source = 'simtrans/_version.py'
versioneer.versionfile_build = 'simtrans/_version.py'
versioneer.tag_prefix = ''
versioneer.parentdir_prefix = 'simtrans-'

sdformat_include = subprocess.check_output('pkg-config sdformat --cflags-only-I', shell=True).strip().lstrip('-I')

setup(name='simtrans',
      version=versioneer.get_version(),
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
      packages=find_packages(exclude=['tests']),
      package_data={'simtrans': ['template/*']},
      ext_modules=[
          Extension('simtranssdfhelper',
                    ['simtrans/sdfhelper.cpp'],
                    include_dirs=[sdformat_include],
                    libraries=['sdformat'],
                 )
      ],
    entry_points={
          'console_scripts': [
              'simtrans = simtrans.cli:main',
              'simtrans-checker = simtrans.cli:checker',
              'catxml = simtrans.catxml:main',
              'gzfetch = simtrans.gzfetch:main'
          ]
      },
      cmdclass=versioneer.get_cmdclass(),
      test_suite='nose2.collector.collector')
