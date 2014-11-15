#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import versioneer


versioneer.VCS = 'git'
versioneer.versionfile_source = 'simtrans/_version.py'
versioneer.versionfile_build = 'simtrans/_version.py'
versioneer.tag_prefix = ''
versioneer.parentdir_prefix = 'simtrans-'

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
      packages=['simtrans',
                'OpenHRP',
                'OpenHRP__POA'],
      entry_points={
          'console_scripts': [
              'simtrans = simtrans.cli:main',
              'catxml = simtrans.catxml:main',
              'gzfetch = simtrans.gzfetch:main'
          ]
      },
      install_requires=['python-graph-core'],
      cmdclass=versioneer.get_cmdclass(),
      test_suite='nose2.collector.collector')
