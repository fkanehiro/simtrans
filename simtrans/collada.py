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
        >>> m = r.read('/opt/ros/indigo/share/atlas_description/meshes/head.dae')
        '''
        m = model.MeshModel()
        d = collada.Collada(f)

        #for i in d.images:
        #    i.path
        for g in d.geometries:
            gm = model.GeometryModel()
            for p in g.primitives:
                gm.vertex = p.vertex
                gm.vertex_index = p.vertex_index
                gm.normal = p.normal
                gm.normal_index = p.normal_index
                # m.material = p.material
                # m.uvmap = p.texcoordset
            m.geometries.append(gm)
        #for e in d.effects:
        #    e.ambient
        return m


class ColladaWriter:
    def write(self, m, f):
        pass
