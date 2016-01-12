#!/usr/bin/env python

import doctest
import simtrans.utils
import simtrans.model
import simtrans.collada
import simtrans.urdf
import simtrans.sdf
import simtrans.vrml
import simtrans.graphviz

import logging
logging.basicConfig(level=logging.DEBUG)
try:
    import coloredlogs
    coloredlogs.install(show_hostname=False, show_name=False)
    coloredlogs.set_level(logging.DEBUG)
except:
    pass

import os
import subprocess

hrpprefix = subprocess.check_output('pkg-config openhrp3.1 --variable=prefix', shell=True).strip()
os.environ['OPENHRP_MODEL_PATH'] = hrpprefix + '/share/OpenHRP-3.1/sample/model'

doctest.testmod(simtrans.utils)
doctest.testmod(simtrans.model)
doctest.testmod(simtrans.collada)
doctest.testmod(simtrans.urdf)
doctest.testmod(simtrans.sdf)
doctest.testmod(simtrans.vrml)
doctest.testmod(simtrans.graphviz)
