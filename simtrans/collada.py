# -*- coding:utf-8 -*-

"""
Reader and writer for collada format
"""

from __future__ import absolute_import
from . import model
import collada
import jinja2


class ColladaReader:
    '''
    Collada reader class
    '''
    def read(self, f):
        '''
        Read collada model data given the file path

        >>> r = ColladaReader()
        >>> r.read('/opt/ros/indigo/share/atlas_description/meshes/head.dae')
        <class 'simtrans.model.MeshModel'>
        '''
        m = model.MeshModel
        d = collada.Collada(f)

        for i in d.images:
            i.path
        for g in d.geometries:
            for p in g.primitives:
                m.vertex = p.vertex
                m.vertex_index = p.vertex_index
                m.normal = p.normal
                m.normal_index = p.normal_index
                # m.material = p.material
                # m.uvmap = p.texcoordset
        for e in d.effects:
            e.ambient
        return m

class ColladaWriter:
    def write(self, m, f):
        pass
