# -*- coding:utf-8 -*-

"""
Reader and writer for stl format
"""

from __future__ import absolute_import
from . import model
from . import collada
import numpy
import os
import subprocess
import tempfile
from stl import stl


class STLReader(object):
    '''
    STL reader class
    '''
    def read(self, f):
        '''
        Read mesh model in STL format
        '''
        m = model.ShapeModel()
        m.shapeType = model.ShapeModel.SP_MESH
        m.data = model.MeshData()
        p = stl.StlMesh(f)
        npoints = p.v0.shape[0]
        idx = numpy.array(range(0, npoints))
        m.data.vertex = numpy.concatenate([p.v0, p.v1, p.v2])
        m.data.vertex_index = numpy.vstack([idx, idx+npoints, idx+2*npoints]).T
        return m


class STLWriter(object):
    '''
    STL writer class
    '''
    def write(self, m, f):
        '''
        Write mesh model in STL format
        This method first generates collada and use meshlab to output stl
        '''
        fd, daefile = tempfile.mkstemp(suffix='.dae')
        os.close(fd)
        cwriter = collada.ColladaWriter()
        cwriter.write(m, daefile)
        subprocess.check_output(['meshlabserver', '-i', daefile, '-o', f])
        os.unlink(daefile)
