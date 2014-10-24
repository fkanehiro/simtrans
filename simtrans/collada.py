# -*- coding:utf-8 -*-

"""
Reader and writer for collada format
"""

from __future__ import absolute_import
from . import model
try:
    from .thridparty import transformations as tf
except UserWarning:
    pass
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
        for c in d.children:
            if type(c) == collada.scene.Node:
                dmat = tf.decompose_matrix(c.matrix)
                m.trans = dmat[3].tolist()
                m.rot = tf.quaternion_from_matrix(tf.compose_matrix(angles=dmat[2]))
                m.children.append(self.convertchildren(c))
            elif type(c) == collada.scene.GeometryNode:
                mm = model.ShapeModel()
                mm.shapeType = model.ShapeModel.SP_MESH
                for p in c.geometry.primitives:
                    gm = model.MeshModel()
                    gm.vertex = p.vertex
                    gm.vertex_index = p.vertex_index
                    gm.normal = p.normal
                    gm.normal_index = p.normal_index
                    # gm.material = p.material
                    # gm.uvmap = p.texcoordset
                    mm.children.append(gm)
                m.children.append(mm)
        return m


class ColladaWriter:
    def write(self, m, f):
        pass
