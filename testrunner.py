#!/usr/bin/env python

import doctest
import simtrans.collada
import simtrans.urdf
import simtrans.sdf
import simtrans.vrml

doctest.testmod(simtrans.collada)
doctest.testmod(simtrans.urdf)
doctest.testmod(simtrans.sdf)
doctest.testmod(simtrans.vrml)
