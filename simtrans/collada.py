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
        d = collada.Collada(f)
        m = model.ShapeModel()
        m.shapeType = model.ShapeModel.SP_NONE
        for n in d.scene.nodes:
            m.children.append(self.convertchildren(n))
        return m

    def convertchildren(self, d):
        m = model.ShapeModel()
        m.shapeType = model.ShapeModel.SP_NONE
        if len(d.transforms) > 0:
            m.matrix = d.transforms[0].matrix
        for c in d.children:
            if type(c) == collada.scene.Node:
                m.children.append(self.convertchildren(c))
            elif type(c) == collada.scene.GeometryNode:
                gm = model.MeshModel()
                for p in c.geometry.primitives:
                    gm.vertex = p.vertex
                    gm.vertex_index = p.vertex_index
                    gm.normal = p.normal
                    gm.normal_index = p.normal_index
                    # gm.material = p.material
                    # gm.uvmap = p.texcoordset
                mm = model.ShapeModel()
                mm.shapeType = model.ShapeModel.SP_MESH
                mm.children.append(gm)
                m.children.append(mm)
        return m


class ColladaWriter:
    def write(self, m, f):
        pass
