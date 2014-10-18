#!/usr/bin/env python

import doctest
import simtrans.collada
import simtrans.urdf
import simtrans.vrml

doctest.testmod(simtrans.collada)
doctest.testmod(simtrans.urdf)
doctest.testmod(simtrans.vrml)
