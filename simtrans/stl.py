# -*- coding:utf-8 -*-

"""Reader and writer for stl format

:Organization:
 AIST

Requirements
------------
* numpy
* numpy-stl
* meshlab
"""

from __future__ import absolute_import
from . import model
from . import collada
import numpy
import os
import subprocess
import tempfile
import logging
from stl import stl


class STLReader(object):
    '''
    STL reader class
    '''
    def read(self, f, assethandler=None, options=None):
        '''
        Read mesh model in STL format
        '''
        data = model.MeshData()
        #stl.MAX_COUNT = 1e10
        p = stl.StlMesh(f)
        npoints = p.v0.shape[0]
        idx = numpy.array(range(0, npoints))
        data.vertex = numpy.concatenate([p.v0, p.v1, p.v2])
        data.vertex_index = numpy.vstack([idx, idx+npoints, idx+2*npoints]).T
        return data


class STLWriter(object):
    '''
    STL writer class
    '''
    def write(self, m, f, options=None):
        '''
        Write mesh model in STL format
        This method first generates collada and use meshlab to output stl
        '''
        fd, daefile = tempfile.mkstemp(suffix='.dae')
        os.close(fd)
        cwriter = collada.ColladaWriter()
        cwriter.write(m, daefile)
        try:
            output = subprocess.check_output(['meshlabserver', '-i', daefile, '-o', f], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            logging.error("meshlabserver returned error: %s" % e.output)
            raise
        except OSError:
            logging.error("command meshlabserver not found. please install by:")
            logging.error("$ sudo apt-get install meshlab")
            raise
        os.unlink(daefile)
