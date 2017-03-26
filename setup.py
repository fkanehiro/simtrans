#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages, Extension
from distutils.version import StrictVersion
import versioneer
import subprocess

versioneer.VCS = 'git'
versioneer.versionfile_source = 'simtrans/_version.py'
versioneer.versionfile_build = 'simtrans/_version.py'
versioneer.tag_prefix = ''
versioneer.parentdir_prefix = 'simtrans-'


sdformat_include = map(lambda x:x.lstrip('-I'), subprocess.check_output('pkg-config sdformat --cflags-only-I', shell=True).strip().split(' '))
sdformat_version = subprocess.check_output('pkg-config sdformat --modversion', shell=True).strip()
if StrictVersion(sdformat_version) >= StrictVersion("4.0.0"): #ubuntu16
    sdformat_compile_args = ['-std=c++11']
else:
    sdformat_compile_args = []

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
                    include_dirs=sdformat_include,
                    libraries=['sdformat'],
                    extra_compile_args=sdformat_compile_args
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
