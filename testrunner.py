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

doctest.testmod(simtrans.utils)
doctest.testmod(simtrans.model)
doctest.testmod(simtrans.collada)
doctest.testmod(simtrans.urdf)
doctest.testmod(simtrans.sdf)
doctest.testmod(simtrans.vrml)
doctest.testmod(simtrans.graphviz)
