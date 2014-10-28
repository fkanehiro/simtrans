# -*- coding:utf-8 -*-

"""
Reader and writer for stl format
"""

from __future__ import absolute_import
from . import model
import numpy
from stl import stl


class STLReader:
    def read(self, f):
        m = model.MeshModel
        p = stl.StlMesh(f)
        npoints = p.v0.shape[0]
        idx = numpy.array(range(0, npoints))
        m.vertex = numpy.concatenate([p.v0, p.v1, p.v2])
        m.vertex_index = numpy.vstack([idx, idx+npoints, idx+2*npoints]).T
        return m


class STLWriter:
    def write(self, m, f):
        pass
